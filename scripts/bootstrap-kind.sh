#!/bin/bash
set -e
echo "=== PRISM Day 1 - Bootstrap Kind Control Plane (Basics) ==="
if kind get clusters | grep -q aiops-m5; then
  echo "Cluster aiops-m5 exists, deleting for clean rebuild"
  kind delete cluster --name aiops-m5
fi
kind create cluster --config k8s/kind-config.yaml
kubectl cluster-info --context kind-aiops-m5
kubectl get nodes -o wide
kubectl apply -f k8s/00-namespace.yaml
kubectl get ns aiops-m5
echo "Kind control plane ready - this is your ONLY control panel"
echo "Next: kubectl get pods -n aiops-m5"
