import socket
import threading
import time
import os
import sys

# Print with timestamps and flush immediately
def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

log("Server starting up...")

# Setup the server
server_ip = "0.0.0.0"  # listen on all interfaces
server_port = 5000

# This keeps track of what number we're on - START WITH 1
global num
num = 1

log(f"Initializing on {server_ip}:{server_port} with num={num}")

# Make sure we have a log file
try:
    if not os.path.exists("messages.txt"):
        log("Creating messages log file")
        with open("messages.txt", "w") as f:
            f.write("=== Message Log ===\n")
    else:
        log("Messages log file exists")
except Exception as e:
    log(f"WARNING: Could not access log file: {e}")

# This converts numbers to words
def num2word(n):
    # I'm just doing 1-15 for this project
    if n == 1: return "one"
    elif n == 2: return "two"
    elif n == 3: return "three"
    elif n == 4: return "four"
    elif n == 5: return "five"
    elif n == 6: return "six"
    elif n == 7: return "seven"
    elif n == 8: return "eight"
    elif n == 9: return "nine"
    elif n == 10: return "ten"
    elif n == 11: return "eleven"
    elif n == 12: return "twelve"
    elif n == 13: return "thirteen"
    elif n == 14: return "fourteen"
    elif n == 15: return "fifteen"
    else: return "number_" + str(n)  # for any other numbers

# For debugging
def print_turn_info():
    global num
    log(f"TURN INFO: Current num={num}")
    log(f"If client_id=1, my_turn={num % 2 == 1}")
    log(f"If client_id=2, my_turn={num % 2 == 0}")

# Handle each client in a separate thread
def client_thread(conn, addr):
    global num
    
    # First, find out which client this is
    try:
        log(f"Sending HELLO to new client from {addr}")
        conn.send(b"HELLO")
        data = conn.recv(1024)
        if not data:
            log(f"No data received from {addr}")
            conn.close()
            return
            
        client_id = int(data.decode().strip())
        log(f"Client {client_id} connected from {addr}")
        print_turn_info()  # Debug info
    except Exception as e:
        log(f"Failed to get client ID from {addr}: {e}")
        try:
            conn.close()
        except:
            pass
        return
    
    # Main client loop
    while True:
        try:
            # Check whose turn it is
            my_turn = False
            if client_id == 1 and num % 2 == 1:  # Client 1 and odd number
                my_turn = True
                log(f"It IS client {client_id}'s turn (num={num})")
            elif client_id == 2 and num % 2 == 0:  # Client 2 and even number
                my_turn = True
                log(f"It IS client {client_id}'s turn (num={num})")
            else:
                log(f"Not client {client_id}'s turn (num={num})")
                
            if my_turn:
                # It's this client's turn
                word = num2word(num)
                msg = "SEND:" + word
                log(f"Sending {msg} to client {client_id}")
                conn.send(msg.encode())
                
                # Get the client's response
                log(f"Waiting for response from client {client_id}")
                response = conn.recv(1024)
                if not response:
                    log(f"Empty response from client {client_id}, disconnecting")
                    break
                    
                response = response.decode().strip()
                log(f"Received '{response}' from client {client_id}")
                
                if response == word:
                    # They sent the right word
                    log(f"Client {client_id} sent correct word: {response}")
                    
                    # Save to our log file
                    try:
                        with open("messages.txt", "a") as f:
                            f.write(f"Client {client_id}: {response}\n")
                        log(f"Saved message to log file")
                    except Exception as e:
                        log(f"Error writing to log file: {e}")
                    
                    # Update our counter
                    num += 1
                    log(f"Updated counter to {num}")
                    print_turn_info()  # Debug info
                    
                    # Tell client it was good
                    log(f"Sending GOOD to client {client_id}")
                    conn.send(b"GOOD")
                else:
                    # Wrong response
                    log(f"Client {client_id} sent wrong word: {response}")
                    conn.send(b"BAD")
            else:
                # Not this client's turn
                log(f"Sending WAIT to client {client_id}")
                conn.send(b"WAIT")
                time.sleep(1)  # don't spam them
        
        except ConnectionResetError:
            log(f"Client {client_id} disconnected abruptly")
            break
        except BrokenPipeError:
            log(f"Connection to client {client_id} was broken")
            break
        except Exception as e:
            log(f"Error with client {client_id}: {e}")
            break
    
    # Clean up
    try:
        conn.close()
    except:
        pass
    log(f"Client {client_id} thread ended")

# Main server code
log("Setting up server socket...")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((server_ip, server_port))
    s.listen(5)
    log(f"Server ready on port {server_port}")
except Exception as e:
    log(f"Fatal error setting up server: {e}")
    sys.exit(1)

# Accept connections forever
while True:
    try:
        log("Waiting for new connections...")
        client, address = s.accept()
        log(f"New connection from {address}")
        
        # Create a new thread for this client
        t = threading.Thread(target=client_thread, args=(client, address))
        t.daemon = True  # so thread dies when main thread dies
        t.start()
        log(f"Started thread for client from {address}")
        
    except KeyboardInterrupt:
        log("Shutting down due to keyboard interrupt...")
        break
    except Exception as e:
        log(f"Error in main loop: {e}")

log("Server shutting down...")
s.close()
EOF
