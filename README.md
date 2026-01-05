🚀 Step-by-Step: Highly Available Multi-Tier Application on AWS EKS

This project demonstrates how to deploy a highly available multi-tier application on AWS EKS, consisting of:

a backend service

a frontend service

Kubernetes Deployments

Kubernetes Services

an AWS Load Balancer

The frontend calls the backend using Kubernetes service discovery.

✅ Prerequisites

Before starting, make sure you have:

AWS account

AWS CLI configured (aws configure)

Docker installed & Docker Hub account

kubectl installed

eksctl installed

An AWS IAM user with EKS permissions

STEP 1️⃣ Create the EKS Cluster

Create an EKS cluster with 2 worker nodes.

eksctl create cluster `
  --name learning-cluster `
  --region ap-south-1 `
  --nodegroup-name workers `
  --node-type t3.small `
  --nodes 2 `
  --nodes-min 2 `
  --nodes-max 2 `
  --managed


Wait until the cluster is fully created.

STEP 2️⃣ Configure kubectl to Use EKS

Update kubeconfig so kubectl talks to AWS EKS (not Docker Desktop).

aws eks update-kubeconfig --region ap-south-1 --name learning-cluster


Verify context:

kubectl config current-context


You should see something like:

arn:aws:eks:ap-south-1:<account-id>:cluster/learning-cluster


Verify nodes:

kubectl get nodes

STEP 3️⃣ Deploy the Backend
Backend Deployment (backend_deployment.yaml)
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


Apply it:

kubectl apply -f backend_deployment.yaml

Backend Service (backend_service.yaml)
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


Apply it:

kubectl apply -f backend_service.yaml


Verify:

kubectl get pods
kubectl get svc


Backend is now:

Highly available (2 replicas)

Accessible inside the cluster only

STEP 4️⃣ Create the Frontend Application
Frontend App (app.py)
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

Requirements (requirements.txt)
flask
requests

STEP 5️⃣ Build & Push Frontend Docker Image
Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]


Build the image:

docker build -t <your-dockerhub-username>/frontend-demo .


Push to Docker Hub:

docker push <your-dockerhub-username>/frontend-demo

STEP 6️⃣ Deploy the Frontend
Frontend Deployment (frontend_deployment.yaml)
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


Apply it:

kubectl apply -f frontend_deployment.yaml


Verify:

kubectl get pods


You should now see frontend + backend pods.

STEP 7️⃣ Expose Frontend to the Internet
Frontend Service (frontend_service.yaml)
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


Apply it:

kubectl apply -f frontend_service.yaml

STEP 8️⃣ Access the Application

Get the Load Balancer URL:

kubectl get svc


Copy the EXTERNAL-IP (ELB DNS) and open it in your browser.

You should see:

“Frontend”

Backend response

Backend pod name (proves load balancing)

STEP 9️⃣ What This Proves

This setup demonstrates:

Multi-tier architecture

Frontend → Backend communication via Service DNS

High availability using replicas

AWS Load Balancer integration

Kubernetes service discovery

Stateless containerized applications

STEP 🔟 Cleanup (IMPORTANT)

To avoid AWS charges:

eksctl delete cluster --name learning-cluster --region ap-south-1


This deletes:

EKS cluster

EC2 nodes

Load balancer

Networking resources