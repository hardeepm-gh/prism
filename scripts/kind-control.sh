#!/bin/bash
set -e
CMD=${1:-health}
case $CMD in
  up)
    ./scripts/bootstrap-kind.sh
    ;;
  down)
    kind delete cluster --name aiops-m5
    ;;
  health)
    kubectl cluster-info --context kind-aiops-m5 || echo "Cluster not running - run ./scripts/bootstrap-kind.sh"
    kubectl get nodes 2>/dev/null || true
    kubectl get ns aiops-m5 2>/dev/null || echo "Namespace not created yet"
    kubectl get pods -n aiops-m5 2>/dev/null || echo "No pods yet - Day 0 is control plane only"
    ;;
  inventory)
    ./scripts/inventory-local.sh
    ;;
  *)
    echo "Usage: $0 {up|down|health|inventory}"
    ;;
esac
