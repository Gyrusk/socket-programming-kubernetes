# Socket Programming with Kubernetes

A distributed messaging system implemented using Python sockets and deployed with Kubernetes. The system includes a server and two clients exchanging numbered messages in a turn-based manner.

---

## Architecture

This system demonstrates:
- TCP socket-based communication
- Kubernetes deployment with 3 pods (1 server, 2 clients)
- Turn-taking mechanism based on even/odd counter logic

---

## Prerequisites

Before starting, ensure you have:
- Docker installed
- Kubernetes cluster (e.g., Minikube, kind, or cloud provider)
- `kubectl` configured

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Gyrusk/socket-programming-kubernetes.git
cd socket-programming-kubernetes
```

### 2. Build Docker Images

```bash
# Build server image
docker build -t socket-server:latest -f Dockerfile.server .

# Build client image
docker build -t socket-client:latest -f Dockerfile.client .
```

### 3. Push Docker Images (if using a remote cluster)

```bash
# Tag images
docker tag socket-server:latest [YOUR_REGISTRY]/socket-server:latest
docker tag socket-client:latest [YOUR_REGISTRY]/socket-client:latest

# Push images
docker push [YOUR_REGISTRY]/socket-server:latest
docker push [YOUR_REGISTRY]/socket-client:latest
```

### 4. Deploy to Kubernetes

```bash
# Update image names in kubernetes.yaml if using a remote registry
kubectl apply -f kubernetes.yaml
```

### 5. Verify Deployment

```bash
# Check that all pods are running
kubectl get pods

# Check that the server service is created
kubectl get svc
```

---

## System Functionality

### Turn-Based Messaging
- The server maintains a counter to assign turns.
- Client 1 sends messages when the counter is odd.
- Client 2 sends messages when the counter is even.

### Commands
- `SEND:number_X` – tells a client to send the message
- `WAIT` – tells a client to wait for its turn
- `GOOD` – server acknowledges correct message

### Message Logging
The server writes all valid messages to a file called `message_log.txt` inside the container.

#### Accessing the Log File

```bash
# Get the name of the server pod
SERVER_POD=$(kubectl get pod -l app=server -o jsonpath="{.items[0].metadata.name}")

# View the log file inside the pod
kubectl exec -it $SERVER_POD -- cat /app/message_log.txt

# Or copy it to your local machine
kubectl cp $SERVER_POD:/app/message_log.txt ./message_log.txt
```

---

## Viewing Logs

```bash
# Server logs
kubectl logs -f $(kubectl get pod -l app=server -o jsonpath="{.items[0].metadata.name}")

# Client 1 logs
kubectl logs -f $(kubectl get pod -l app=client1 -o jsonpath="{.items[0].metadata.name}")

# Client 2 logs
kubectl logs -f $(kubectl get pod -l app=client2 -o jsonpath="{.items[0].metadata.name}")
```

### Multi-Pane Log Monitoring with tmux (Optional)

```bash
# Install tmux
sudo apt install tmux

# Start a new tmux session
tmux

# Split panes for logs
tmux new-session \; split-window -v \; split-window -h \; select-pane -t 0

# Use these in each pane:
# kubectl logs -f <server-pod>
# kubectl logs -f <client1-pod>
# kubectl logs -f <client2-pod>
```

---

## Stopping the System

```bash
# Delete everything
kubectl delete -f kubernetes.yaml
```

Or delete individual components:

```bash
kubectl delete deployment server-deployment
kubectl delete deployment client1-deployment
kubectl delete deployment client2-deployment
kubectl delete service server-service
```

---

## Troubleshooting

### Clients Can't Connect
- Make sure the server service is running: `kubectl get svc`
- Confirm that the service name in client code matches the Kubernetes service

### Getting "GOODWAIT"
This is expected if the server sends multiple commands quickly in a row

### Pods Not Responding

```bash
# Restart server or clients
kubectl rollout restart deployment server-deployment
kubectl rollout restart deployment client1-deployment
kubectl rollout restart deployment client2-deployment
```

---

## Credits
Created as a demo of distributed socket programming using Python and Kubernetes.

