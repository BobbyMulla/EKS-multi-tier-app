# 🚀 Highly Available Multi-Tier Application on AWS EKS

This project demonstrates how to deploy a **highly available multi-tier application** on **AWS EKS**, consisting of:

- Backend service
- Frontend service
- Kubernetes Deployments
- Kubernetes Services
- AWS Load Balancer

The frontend communicates with the backend using **Kubernetes service discovery (DNS)**.

---

## ✅ Prerequisites

Before starting, ensure you have:

- AWS account
- AWS CLI configured (`aws configure`)
- Docker installed + Docker Hub account
- kubectl installed
- eksctl installed
- IAM user with EKS permissions

---

## STEP 1️⃣ Create the EKS Cluster

Create an EKS cluster with two worker nodes.

```powershell
eksctl create cluster `
  --name learning-cluster `
  --region ap-south-1 `
  --nodegroup-name workers `
  --node-type t3.small `
  --nodes 2 `
  --nodes-min 2 `
  --nodes-max 2 `
  --managed
````

Wait until the cluster creation completes.

---

## STEP 2️⃣ Configure kubectl to Use EKS

Update kubeconfig so kubectl talks to AWS EKS (not Docker Desktop).

```powershell
aws eks update-kubeconfig --region ap-south-1 --name learning-cluster
```

Verify context:

```powershell
kubectl config current-context
```

Verify nodes:

```powershell
kubectl get nodes
```

---

## STEP 3️⃣ Deploy the Backend

### Backend Deployment (`backend_deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: nginxdemos/hello
```

Apply it:

```powershell
kubectl apply -f backend_deployment.yaml
```

---

### Backend Service (`backend_service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - port: 80
      targetPort: 80
```

Apply it:

```powershell
kubectl apply -f backend_service.yaml
```

Verify:

```powershell
kubectl get pods
kubectl get svc
```

---

## STEP 4️⃣ Create the Frontend Application

### Frontend App (`app.py`)

```python
from flask import Flask
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-service")

@app.route("/")
def home():
    response = requests.get(BACKEND_URL)
    return f"""
    <h1>Frontend</h1>
    <p>Response from backend:</p>
    <pre>{response.text}</pre>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
```

### Requirements (`requirements.txt`)

```txt
flask
requests
```

---

## STEP 5️⃣ Build & Push Frontend Docker Image

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

Build and push:

```powershell
docker build -t <your-dockerhub-username>/frontend-demo .
docker push <your-dockerhub-username>/frontend-demo
```

---

## STEP 6️⃣ Deploy the Frontend

### Frontend Deployment (`frontend_deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: <your-dockerhub-username>/frontend-demo
        env:
        - name: BACKEND_URL
          value: http://backend-service
        ports:
        - containerPort: 80
```

Apply it:

```powershell
kubectl apply -f frontend_deployment.yaml
```

Verify:

```powershell
kubectl get pods
```

---

## STEP 7️⃣ Expose Frontend to the Internet

### Frontend Service (`frontend_service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
```

Apply it:

```powershell
kubectl apply -f frontend_service.yaml
```

---

## STEP 8️⃣ Access the Application

Get the LoadBalancer DNS:

```powershell
kubectl get svc
```

Open the **EXTERNAL-IP (ELB DNS)** in your browser.

You should see:

* Frontend page
* Backend response
* Backend pod name (proves load balancing)

---

## STEP 9️⃣ Cleanup (IMPORTANT)

To avoid AWS charges:

```powershell
eksctl delete cluster --name learning-cluster --region ap-south-1
```

This deletes:

* EKS cluster
* EC2 nodes
* Load balancer
* Networking resources