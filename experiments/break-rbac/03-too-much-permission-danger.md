# Experiment 3: Too much permission - cluster-admin danger

## What I did
Gave cluster-admin to correlator-sa

## Result
can delete pods --all-namespaces? YES
can get secrets --all-namespaces? YES

## Why dangerous
If correlator pod is compromised, attacker can:
- Delete kube-system pods → cluster down
- Read all secrets cluster-wide → steal tokens
- Create privileged pods → escape to host

## Learning
NEVER give cluster-admin to service. Use minimal namespace-scoped Role.

## Cleanup
kubectl delete clusterrolebinding correlator-admin
After cleanup: can delete pods? NO again — safe
