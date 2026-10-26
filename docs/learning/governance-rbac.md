# Day 1 - Governance: RBAC Least Privilege - Learning Guide
## Learn → Break → Build → Reflect

> **Objective:** Understand WHY least privilege matters, not just apply yaml. By end of Day 1, you can explain RBAC in interview without reading notes.

---

### PART 1: LEARN - Why RBAC?

#### What is RBAC? (5 min read official docs)
- Read: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- Key: RBAC = Who can do What on Which resources
- 3 objects:
  - **ServiceAccount:** Identity for pod (like user for humans). `correlator-sa` is identity for correlator pod
  - **Role:** What you can do (verbs) on which resources (e.g., get, list configmaps in aiops-m5 namespace)
  - **RoleBinding:** Who gets Role (binds ServiceAccount to Role)

#### Why least privilege for Prism?
- In v7, everything ran as root in Docker, could do anything
- In Prism governed, correlator should NOT be able to delete pods, remediator should NOT list secrets cluster-wide
- If correlator is compromised, attacker can only get configmaps, not delete cluster
- Principle: **If service doesn't need permission, DON'T give it**

#### Questions to answer before building:
1. What is difference between Role vs ClusterRole? (Hint: Role = namespace-scoped, ClusterRole = cluster-scoped)
2. What is difference between RoleBinding vs ClusterRoleBinding?
3. Why ServiceAccount and not User? (Pods use ServiceAccount, humans use User)
4. What happens if pod has no ServiceAccount? (Uses default ServiceAccount in namespace)

#### Official docs to read (15 min):
- https://kubernetes.io/docs/concepts/security/service-accounts/
- https://kubernetes.io/docs/reference/access-authn-authz/rbac/#service-account-permissions

---

### PART 2: BREAK - Hands-On Break Experiments (Most Important!)

**Do these IN ORDER, document what breaks in `experiments/break-rbac/`. Each experiment has expected failure.**

#### Experiment 0: Setup - Check current state

```bash
# Check namespace exists from Day 0
kubectl get ns aiops-m5
kubectl get serviceaccounts -n aiops-m5
# Should show only default SA now

# Check your own permissions (you are admin via kind)
kubectl auth can-i get secrets --all-namespaces
# Should be YES - you are cluster-admin via Kind

# Check what default SA can do (almost nothing)
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:default -n aiops-m5
# Should be NO
```

Document: What can default SA do?

#### Experiment 1: Create ServiceAccount without Role - Should FAIL to get secrets

```bash
kubectl create serviceaccount correlator-sa -n aiops-m5
kubectl get sa correlator-sa -n aiops-m5

# Try to get secrets as correlator-sa (should FAIL - no RoleBinding)
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Expected: NO

# Try to impersonate and actually get secrets
kubectl get secrets -n aiops-m5 --as=system:serviceaccount:aiops-m5:correlator-sa
# Expected: Forbidden error

# Document: SA without RoleBinding = no permissions
```

Create file: `experiments/break-rbac/01-sa-without-role.md` - what error did you see?

#### Experiment 2: Create Role that can get configmaps ONLY, not secrets - Test least privilege

```bash
cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: correlator-role-test
  namespace: aiops-m5
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get","list"]
EOF

kubectl create rolebinding correlator-rb-test --role=correlator-role-test --serviceaccount=aiops-m5:correlator-sa -n aiops-m5

# Now test: can get configmaps? YES
kubectl auth can-i get configmaps --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Expected: YES

kubectl get configmaps -n aiops-m5 --as=system:serviceaccount:aiops-m5:correlator-sa
# Should work (maybe 0 configmaps yet, but no Forbidden)

# Can get secrets? Should FAIL - least privilege!
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Expected: NO

kubectl get secrets -n aiops-m5 --as=system:serviceaccount:aiops-m5:correlator-sa
# Expected: Forbidden

# Document: Role with only configmaps = cannot get secrets - least privilege enforced!
```

Create: `experiments/break-rbac/02-role-configmaps-only.md`

#### Experiment 3: Give too much permission (cluster-admin) - Show why dangerous

```bash
# DANGEROUS - for learning only, in Kind lab is OK
kubectl create clusterrolebinding correlator-admin --clusterrole=cluster-admin --serviceaccount=aiops-m5:correlator-sa

# Now correlator-sa can do EVERYTHING
kubectl auth can-i delete pods --all-namespaces --as=system:serviceaccount:aiops-m5:correlator-sa
# Expected: YES - DANGEROUS!

kubectl auth can-i get secrets --all-namespaces --as=system:serviceaccount:aiops-m5:correlator-sa
# Expected: YES - can get ALL secrets cluster-wide!

# If this SA is compromised, attacker can delete kube-system!
# This is why we DON'T give cluster-admin to services

# Cleanup immediately - revoke cluster-admin
kubectl delete clusterrolebinding correlator-admin

kubectl auth can-i delete pods --all-namespaces --as=system:serviceaccount:aiops-m5:correlator-sa
# Expected: NO again after cleanup

# Document: Why cluster-admin for service is dangerous, real-world breach scenario
```

Create: `experiments/break-rbac/03-too-much-permission-danger.md`

#### Experiment 4: Test remediator-sa minimal Role - Can only get secrets, cannot list pods

```bash
kubectl create serviceaccount remediator-sa -n aiops-m5

cat <<EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: remediator-role-test
  namespace: aiops-m5
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
EOF

kubectl create rolebinding remediator-rb-test --role=remediator-role-test --serviceaccount=aiops-m5:remediator-sa -n aiops-m5

# Can get secrets? YES (needs token)
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:remediator-sa -n aiops-m5
# Expected: YES

# Can list pods? Should FAIL - remediator doesn't need to list pods, only restart allowlisted via API
kubectl auth can-i list pods --as=system:serviceaccount:aiops-m5:remediator-sa -n aiops-m5
# Expected: NO - least privilege!

# Document: remediator-sa minimal = can get secrets (for token) but cannot list pods - good!
```

Create: `experiments/break-rbac/04-remediator-minimal.md`

#### Experiment 5: What if pod runs with default ServiceAccount? (Common mistake)

```bash
# Deploy a pod without specifying serviceAccountName - uses default SA
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: test-default-sa
  namespace: aiops-m5
spec:
  containers:
  - name: busybox
    image: busybox:1.35
    command: ["sleep", "3600"]
EOF

kubectl get pod test-default-sa -n aiops-m5

# What SA does it use?
kubectl get pod test-default-sa -n aiops-m5 -o jsonpath='{.spec.serviceAccountName}'
# Expected: default

# Can default SA get secrets?
kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:default -n aiops-m5
# Expected: NO

# So pod with default SA cannot get secrets - if your app needs secrets, it will fail!

# Cleanup
kubectl delete pod test-default-sa -n aiops-m5

# Document: Why we must specify serviceAccountName in Deployment
```

Create: `experiments/break-rbac/05-default-sa-fails.md`

---

### PART 3: BUILD - Now Build From Memory (Not Copy)

**After breaking, you understand WHY. Now build yourself, without copying my yaml.**

#### Task: Create `k8s/01-governance-rbac.yaml` from scratch

Requirements (from what you learned):
- 3 ServiceAccounts: correlator-sa, remediator-sa, approval-gateway-sa in namespace aiops-m5
- Role correlator-role: can get,list configmaps and get secrets (needs secrets for token, configmaps for config)
- Role remediator-role: can get secrets only (for token)
- Role approval-gateway-role: can get secrets + configmaps (needs policies ConfigMap + secrets)
- RoleBindings: bind each SA to its Role
- NO ClusterRole, NO cluster-admin, namespace-scoped only

Steps:

1. Write yaml file from memory (don't copy, try first):
```bash
cat > k8s/01-governance-rbac.yaml <<'EOF'
# Try to write yourself - include ServiceAccount, Role, RoleBinding for each
# If stuck, check kubectl create serviceaccount --help, kubectl create role --help
EOF
```

2. Apply:
```bash
kubectl apply -f k8s/01-governance-rbac.yaml
kubectl get serviceaccounts,roles,rolebindings -n aiops-m5
```

3. Validate least privilege:
```bash
kubectl auth can-i get configmaps --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Should be YES

kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Should be YES (needs token)

kubectl auth can-i list pods --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Should be NO - least privilege! correlator doesn't need to list pods

kubectl auth can-i get secrets --as=system:serviceaccount:aiops-m5:remediator-sa -n aiops-m5
# Should be YES

kubectl auth can-i list pods --as=system:serviceaccount:aiops-m5:remediator-sa -n aiops-m5
# Should be NO - remediator doesn't need to list pods, only restart allowlisted via API

kubectl auth can-i delete pods --all-namespaces --as=system:serviceaccount:aiops-m5:correlator-sa -n aiops-m5
# Should be NO - not cluster-admin!
```

4. If validation fails, fix yaml, re-apply, re-test. Document mistakes in daily log.

#### Expected final file structure (compare after you build yourself):

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: correlator-sa
  namespace: aiops-m5
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: correlator-role
  namespace: aiops-m5
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get","list"]
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: correlator-rb
  namespace: aiops-m5
subjects:
- kind: ServiceAccount
  name: correlator-sa
  namespace: aiops-m5
roleRef:
  kind: Role
  name: correlator-role
  apiGroup: rbac.authorization.k8s.io
# ... repeat for remediator-sa, approval-gateway-sa
```

---

### PART 4: REFLECT - Teach It Back

Create `docs/learning/day-1-governance-rbac.md`:

```markdown
# Day 1 - Governance RBAC Least Privilege

## What I thought before:
RBAC is just username/password for K8s

## What I learned by breaking:
- Experiment 1: SA without RoleBinding = no permissions, Forbidden error
- Experiment 2: Role with only configmaps = can get configmaps YES, secrets NO - least privilege enforced
- Experiment 3: Gave cluster-admin to correlator-sa, it could delete pods --all-namespaces YES - DANGEROUS! If compromised, attacker owns cluster. Revoked immediately.
- Experiment 4: remediator-sa minimal Role can get secrets YES but list pods NO - good, doesn't need to list pods
- Experiment 5: Pod with default SA cannot get secrets, fails - must specify serviceAccountName in Deployment

## What I built:
k8s/01-governance-rbac.yaml with 3 SAs, each Role minimal, no cluster-admin, namespace-scoped

## Interview answer (without reading notes):
"RBAC is least privilege: ServiceAccount is identity for pod, Role defines what verbs on which resources in namespace, RoleBinding binds SA to Role. I use minimal Roles: correlator-sa can get configmaps/secrets only, not list pods or delete, remediator-sa can get secrets only. I never give cluster-admin to services because if compromised, attacker can delete kube-system. I validate with kubectl auth can-i --as=system:serviceaccount:aiops-m5:correlator-sa"

## Questions remaining:
- How does K8s audit RBAC denials? Where are logs?
- What is difference between Role and ClusterRole in real prod with multiple namespaces?
- How to rotate ServiceAccount tokens?

## Next: Why NetworkPolicy default-deny needed even with RBAC? (Day 1 afternoon)
```

Also create `docs/daily-log/2026-05-14.md`:

```markdown
# Day 1 - 2026-05-14 - Governance RBAC

## Done
- 5 break experiments: SA without Role, configmaps-only Role, cluster-admin danger, remediator minimal, default SA fails
- Built k8s/01-governance-rbac.yaml from memory after breaking
- Validated with kubectl auth can-i

## What broke
- Initially gave correlator-role list pods - realized correlator doesn't need to list pods, only get configmaps/secrets - removed list pods - least privilege

## What learned
- RBAC least privilege = SA + minimal Role + RoleBinding, no cluster-admin for services

## Next: NetworkPolicies default-deny
```

---

### Validation Checklist for Day 1

- [ ] 5 experiments in experiments/break-rbac/ with what error you saw
- [ ] k8s/01-governance-rbac.yaml built from memory (not copied)
- [ ] kubectl auth can-i tests all pass per least privilege (correlator can get configmaps/secrets YES, list pods NO, delete all-namespaces NO)
- [ ] docs/learning/day-1-governance-rbac.md with interview answer
- [ ] docs/daily-log/2026-05-14.md
- [ ] git add -A && git commit -m "feat(day-1): governance RBAC - Learn/Break/Build/Reflect - least privilege" && git push
- [ ] CI green

---

### Resources

- Official: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- ServiceAccounts: https://kubernetes.io/docs/concepts/security/service-accounts/
- kubectl auth: https://kubernetes.io/docs/reference/access-authn-authz/authorization/#checking-api-access
- Least privilege: https://kubernetes.io/docs/concepts/security/rbac-good-practices/

---

### Tomorrow Preview: Day 1 Afternoon - NetworkPolicies

Why RBAC not enough? RBAC controls API access, NetworkPolicy controls pod-to-pod network traffic. Even with RBAC, pod can talk to any pod via network. default-deny-all blocks all ingress/egress, then explicit allow only alertmanager→correlator etc. Zero trust.

Experiments: Apply default-deny, try curl from cockpit to correlator - blocked? Remove policy - works. Learn.

---

END OF DAY 1 LEARNING GUIDE
