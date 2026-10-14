# Experiment 1: SA without Role

## Command
kubectl create serviceaccount correlator-sa -n aiops-m5
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5

## Result
NO — no permissions

## Error when trying to get secrets
Forbidden: User "system:serviceaccount:aiops-m5:correlator-sa" cannot list resource "secrets"...

## Learning
SA without RoleBinding = no permissions. Must bind Role to SA.
