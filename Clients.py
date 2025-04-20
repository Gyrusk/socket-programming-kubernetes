import socket
import time
import random
import sys
import os

# Print with timestamps and flush immediately
def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

# Server info
SERVER = os.environ.get("SERVER_HOST", "localhost")
PORT = 5000

# Figure out which client we are
if len(sys.argv) > 1:
    client_id = int(sys.argv[1])
else:
    client_id = int(os.environ.get("CLIENT_ID", "1"))

log(f"Starting client {client_id}")
log(f"Will connect to server at {SERVER}:{PORT}")

# Connect to server
while True:
    try:
        log(f"Trying to connect to server at {SERVER}:{PORT}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER, PORT))
        log("Successfully connected to server")
        
        # Get greeting and send ID
        log("Waiting for server greeting")
        greeting = s.recv(1024)
        if not greeting:
            log("Received empty greeting from server")
            s.close()
            raise ConnectionError("Empty response from server")
            
        greeting = greeting.decode()
        log(f"Server sent: '{greeting}'")
        
        if greeting == "HELLO":
            log(f"Sending my ID: {client_id}")
            s.send(str(client_id).encode())
            log(f"ID sent successfully")
        else:
            log(f"Unexpected greeting: '{greeting}'")
        
        # Main loop
        log("Entering main communication loop")
        while True:
            log("Waiting for server command")
            data = s.recv(1024)
            
            if not data:
                log("Server disconnected (empty message)")
                break
                
            data = data.decode()
            log(f"Server sent: '{data}'")
                
            if data.startswith("SEND:"):
                # Server wants us to send a word
                word = data[5:]  # remove "SEND:" prefix
                log(f"Server wants me to send: '{word}'")
                
                # Wait a bit (simulate thinking)
                wait_time = random.uniform(0.5, 2)
                log(f"Thinking for {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                
                # Send it
                log(f"Sending: '{word}'")
                s.send(word.encode())
                
                # Get server's response
                log("Waiting for server's response")
                reply = s.recv(1024)
                if not reply:
                    log("Server disconnected after I sent word")
                    break
                
                reply = reply.decode()
                log(f"Server replied: '{reply}'")
                
                if reply == "GOOD":
                    log("Server accepted my message")
                elif reply == "BAD":
                    log("Server rejected my message")
                else:
                    log(f"Unexpected server response: '{reply}'")
                    
            elif data == "WAIT":
                # Not my turn yet
                log("Not my turn yet")
                time.sleep(1)
            else:
                log(f"Unknown server message: '{data}'")
    
    except ConnectionRefusedError:
        log("Connection refused - server might not be running")
    except ConnectionResetError:
        log("Connection reset by server")
    except Exception as e:
        log(f"Error: {e}")
    
    # Wait before trying again
    wait_time = random.randint(3, 8)
    log(f"Will try again in {wait_time} seconds...")
    time.sleep(wait_time)
