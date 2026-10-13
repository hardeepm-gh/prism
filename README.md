# PRISM - Governance-Wrapped Incident Refinery
### Kind-Native • Ground-Up • Learning-First • GitHub-Native

> **From alert storm to single source of truth — with governance, human gating, and audit.**
> Control Plane: Kind cluster `aiops-m5` | Ground-up build, reference architecture only

[[CI](https://github.com/<you>/prism/actions/workflows/ci.yml/badge.svg)](https://github.com/<you>/prism/actions)
[[Governance](https://img.shields.io/badge/governance-enforced-brightgreen)](docs/GOVERNANCE.md)
[[Learning](https://img.shields.io/badge/learning-first-blue)](docs/learning/)

---

## What is Prism?

**Prism refines noise to signal:**

```
[4 Alerts: VM Down, API Down, DB Down, Queue High]
         |
         v
    🔷 PRISM REFINERY (Kind Control Plane)
    ├── Correlation: group_by root_correlation_key = claims-platform-failure
    ├── Suppression: 4 → 1 parent + 3 child suppressed (75% noise reduction)
    ├── RCA Ranking: vm_metrics_down = root cause, others = symptoms
    ├── Governance: RBAC + NetworkPolicy + OPA + Human Gating
    └── Audit: who approved, when, what
         |
         v
[1 Parent Incident | RCA: business-app-vm / vm_metrics_down | Status: pending human approval]
```

**Two scenarios with controlled autonomy:**

| Scenario | Risk | Governance | Human Gating |
|----------|------|------------|--------------|
| **NGINX Closed-Loop** `aiops-demo-nginx` down | Low | Allowlist + Token + Audit | **L3 Auto-approved per policy** (audited, reversible) |
| **Claims VM Multi-Alert** `business-app-vm` down | High | OPA: requires approval_id + allowlist check + Audit | **L4 Human approval required** via Cockpit :8095 / Approval Gateway :8087 / GLPI :8088 |

**No remediation without governance.** Full autonomous with no human intervention is prohibited by OPA policy.

---

## Why Kind as Control Plane?

- **Kind cluster `aiops-m5` is the single control plane:** `kubectl` is the single pane of glass
- **Declarative:** `k8s/*.yaml` + `kind load docker-image` + `kubectl apply -f k8s/` → GitOps-ready
- **Portable:** `extraPortMappings` in `k8s/kind-config.yaml` maps NodePort 30080-30088 → localhost 8095,3006,8088,9090,9093,8089,8085,8087
- **CI-Testable:** GitHub Actions creates the same Kind cluster and validates manifests
- **Ground-up:** No legacy compose, built from `k8s/kind-config.yaml` only

```bash
./scripts/kind-control.sh health
# = kubectl cluster-info + kubectl get nodes + kubectl get pods -n aiops-m5 + kubectl get svc -n aiops-m5
```

---

## Governance Outer Ring - Everything Surrounded by Governance

```
┌──────────────────────────────────────────────────────────────┐
│  GOVERNANCE OUTER RING (wraps everything)                    │
│  ├── RBAC: ServiceAccounts least-privilege                   │
│  ├── Secrets: K8s Secret aiops-secrets, rotation             │
│  ├── NetworkPolicies: default-deny-all + explicit allows     │
│  ├── OPA Policies: allowlist=[aiops-demo-nginx], L3 auto-approved, L4 requires approval_id │
│  ├── Approval Gateway :8087: Human gating service            │
│  ├── Audit: /data/audit + Prometheus aiops_governance_approval_total │
│  └── GLPI ITSM :8088: System of record                       │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  CORE: Signal → Correlate → RCA → Approval → Act      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

- **L3 Auto-approved:** `demo-nginx-down`, low-risk, allowlisted, audited, reversible, `approver: auto-policy-L3`
- **L4 Human approval required:** `claims-platform-failure`, high-risk, needs `X-Token + X-Approval-ID + X-Approver` identity, audit_id, expires_at
- **Remediator enforces:** token + approval_id + allowlist + audit → DENY otherwise

See [docs/GOVERNANCE.md](docs/GOVERNANCE.md)

---

## Learning-First Approach

**Objectives:**
1. Build a production-grade governance-wrapped incident refinery
2. Learn underlying concepts hands-on as a key project

**Learn → Break → Build → Reflect for every component:**

- **LEARN:** Why does this exist? Read official documentation.
- **BREAK:** What if it is removed? Validate failure modes and document.
- **BUILD:** Implement from understanding, not copy-paste, fix via `kubectl logs` and `describe`.
- **REFLECT:** Teach it back in `docs/learning/day-N-xxx.md`.

**Repository holds learning, not just code:**
```
docs/learning/day-0-kind-control-plane.md
docs/learning/day-1-rbac-least-privilege.md
docs/daily-log/ (what was done + what broke + what was learned)
experiments/break-rbac/ (intentional break experiments)
```

---

## Quick Start - Day 0 Basics

### Prerequisites

- Docker (Docker Desktop, Rancher Desktop, or compatible)
- Kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation
- kubectl: https://kubernetes.io/docs/tasks/tools/
- Git and GitHub CLI (optional): https://cli.github.com/

### 1. Folder Structure

```bash
# Clone or initialize the repository
git clone https://github.com/<you>/prism.git
cd prism

# Or create structure locally
chmod +x create-prism-structure.sh
./create-prism-structure.sh

# Expected structure:
# prism/
# ├── k8s/kind-config.yaml + 00-namespace.yaml
# ├── scripts/inventory-local.sh + bootstrap-kind.sh + kind-control.sh
# ├── services/approval-gateway/app/.gitkeep + correlator/app/.gitkeep + cockpit/app/.gitkeep + remediator/app/.gitkeep
# ├── docs/inventory/ + daily-log/ + architecture/ + ROADMAP.md + GOVERNANCE.md
# ├── data/demo/.gitkeep + backups/.gitkeep
# ├── .github/workflows/ci.yml
# ├── .gitignore + README.md + Makefile
```

### 2. Local Inventory

```bash
chmod +x scripts/*.sh
./scripts/inventory-local.sh
cat docs/inventory/LOCAL_INVENTORY.md
# Reports: local folders, available container images, Kind/kubectl versions
```

### 3. GitHub Setup

```bash
git init
git add -A
git commit -m "feat(day-0): basics - folder structure + kind-config + inventory script"

# Create GitHub repository
gh repo create prism --public --source=. --push   --description "Prism - Governance-wrapped incident refinery: Kind-native, 4:1 correlation, human gating"

# Or manually:
# 1. Create repository at github.com/new (name: prism, public, no README)
# 2. git remote add origin https://github.com/<you>/prism.git
# 3. git branch -M main
# 4. git push -u origin main
```

### 4. Bootstrap Kind Control Plane

```bash
./scripts/bootstrap-kind.sh
# Creates Kind cluster using k8s/kind-config.yaml
# Applies k8s/00-namespace.yaml

./scripts/kind-control.sh health
# Validates:
# - Cluster: kind-aiops-m5
# - Nodes: control-plane ready
# - Namespace: aiops-m5
# - Pods: none yet (Day 0 - control plane only)

kubectl cluster-info --context kind-aiops-m5
kubectl get ns aiops-m5
kubectl get nodes -o wide
```

### 5. Daily Log and Push

```bash
cat > docs/daily-log/2026-05-13.md <<'EOF'
# Day 0 - 2026-05-13 - Basics
## Completed
- Folder structure: k8s/, scripts/, services/, docs/, data/, backups/, .github/
- k8s/kind-config.yaml (Kind cluster + extraPortMappings) + 00-namespace.yaml
- scripts/inventory-local.sh + bootstrap-kind.sh + kind-control.sh
- .gitignore configured (secrets, data, backups excluded)
- GitHub repository initialized

## Learning
- Kind runs Kubernetes inside a container: docker ps | grep aiops-m5 shows control-plane
- extraPortMappings exposes NodePort services to localhost
- Control plane components: API server, etcd, scheduler run inside Kind container

## Next
- Day 1: Governance RBAC + Secrets + NetworkPolicies
EOF

git add -A
git commit -m "docs(day-0): daily log + local inventory + learning"
git push

# Validate CI: https://github.com/<you>/prism/actions
```

---

## Roadmap - 14 Days Ground-Up

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed Learn/Break/Build/Reflect plan.

| Day | Focus | Learning Goal | Deliverable | Governance |
|-----|-------|---------------|-------------|------------|
| **0** | Basics | Kind control plane concepts | Folder structure + kind-config + inventory + GitHub | - |
| **1** | RBAC + NetworkPolicies | ServiceAccount, Role, RoleBinding, least privilege, default-deny | 01-rbac.yaml + 04-secrets.yaml + 02-networkpolicies.yaml | RBAC + Secrets + NetworkPolicy |
| **2** | OPA + Approval Gateway | Allowlist, L3 vs L4, human gating | 03-opa-policies.yaml + Approval Gateway :8087 | OPA + Approval Gateway |
| **3** | Prometheus | PromQL, correlation labels | 10-prometheus-config.yaml + 11-prometheus.yaml | - |
| **4** | Alertmanager + Blackbox | group_by root_correlation_key | 20-alertmanager.yaml + 40-blackbox.yaml | - |
| **5** | Correlator Core | Parent/child, RCA ranking, suppression | services/correlator/ + 31-correlator.yaml | - |
| **6** | Integration | Idempotency, safe reset | Correlator → Approval Gateway + reset procedure | - |
| **7** | Cockpit | Visualization + approval action | services/cockpit/ + 32-cockpit.yaml :8095 | Human gating UI |
| **8** | Grafana | Provisioning, datasources | 50-grafana.yaml :3006 dashboards | Audit dashboard |
| **9** | Remediator | Token + approval_id + allowlist + audit | services/remediator/ + 33-remediator.yaml | Token + approval_id + allowlist |
| **10** | ITSM + Target | System of record | 60-glpi.yaml :8088 + 33-demo-nginx.yaml :8085 | GLPI as system of record |
| **11** | Scenario L3 | Controlled autonomy | run-prism-live-demo.sh | L3 auto-approved audited |
| **12** | Scenario L4 | Human judgment | run-claims-multialert-demo.sh | L4 human approval required |
| **13** | Hardening | PVC, backup | PVCs, backup/shutdown scripts, docs | - |
| **14** | Release | Teaching | Demo guide, HLD/LLD, tag v1.0.0-governed | - |

**Daily Workflow:**
```bash
git pull
./scripts/kind-control.sh health
# Implement today's k8s/ manifest after learning
kubectl apply -f k8s/<today>.yaml
kubectl logs -n aiops-m5 deployment/<today> -f
# Document learning
echo "# Day N" > docs/daily-log/$(date +%Y-%m-%d).md
git add -A && git commit -m "feat(day-N): <service>" && git push
```

---

## Architecture

```
Kind Cluster: aiops-m5
├── k8s/kind-config.yaml: extraPortMappings 30080→8095, 30081→3006, 30082→8088, 30083→9090, 30084→9093, 30085→8089, 30086→8085, 30088→8087
├── Namespace: aiops-m5 (governance: enforced)
├── Governance:
│   ├── 01-governance-rbac.yaml: ServiceAccounts + Roles least-privilege
│   ├── 02-governance-networkpolicies.yaml: default-deny-all + explicit allows
│   ├── 03-governance-opa-policies.yaml: allowlist=[aiops-demo-nginx], L3 auto-approved, L4 requires approval_id
│   ├── 04-secrets.yaml: Secret aiops-secrets
│   └── 30-approval-gateway.yaml: :8087 human gating
├── Signal:
│   ├── 11-prometheus.yaml :9090 (NodePort 30083) + 10-prometheus-config.yaml
│   ├── 20-alertmanager.yaml :9093 (NodePort 30084) group_by root_correlation_key
│   └── 40-blackbox.yaml :9115 (NodePort 30087)
├── Intelligence:
│   └── 31-correlator.yaml :8089 (NodePort 30085) parent/child + RCA + approval request
├── Visualization:
│   ├── 32-cockpit.yaml :8095 (NodePort 30080) KPI + RCA + Approve button
│   └── 50-grafana.yaml :3006 (NodePort 30081) Executive + RCA + Governance Audit
├── Controlled Act:
│   ├── 33-remediator.yaml :8090 ClusterIP (requires X-Token + X-Approval-ID + X-Approver)
│   └── 33-demo-nginx.yaml :8085 (NodePort 30086) safe target
└── ITSM:
    └── 60-glpi.yaml :8088 (NodePort 30082) MariaDB + GLPI system of record
```

---

## Service URLs (via Kind NodePort)

| Component | URL | NodePort | Purpose |
|-----------|-----|----------|---------|
| Cockpit | http://localhost:8095 | 30080 | Visual + Approve button + KPI + RCA |
| Approval Gateway | http://localhost:8087 | 30088 | Human gating UI + API + metrics |
| Grafana | http://localhost:3006 | 30081 | Executive + RCA + Governance Audit |
| GLPI | http://localhost:8088 | 30082 | ITSM system of record |
| Prometheus | http://localhost:9090 | 30083 | Metrics + rules + alerts |
| Alertmanager | http://localhost:9093 | 30084 | Grouping by root_correlation_key |
| Correlator | http://localhost:8089 | 30085 | Correlation + RCA + metrics |
| Demo NGINX | http://localhost:8085 | 30086 | Safe remediation target |
| Blackbox | http://localhost:9115 | 30087 | Probes |

---

## Validation

```bash
./scripts/kind-control.sh health
kubectl get pods -n aiops-m5 -o wide
kubectl get svc -n aiops-m5
kubectl get roles,rolebindings,serviceaccounts,networkpolicies,secrets -n aiops-m5

curl -s http://localhost:8087/healthz | jq .  # Approval Gateway
curl -s http://localhost:8089/healthz | jq .  # Correlator
curl -s http://localhost:8095/api/healthz | jq .  # Cockpit
curl -s http://localhost:3006/api/health | jq .  # Grafana
curl -s http://localhost:9090/-/healthy
curl -s http://localhost:8089/root-incidents | jq .
curl -s http://localhost:8087/approvals | jq .
curl -s http://localhost:8089/metrics | grep aiops_
curl -s http://localhost:8087/metrics | grep governance
```

---

## Resume - Key Project

**Repository description:**
> Prism - Kind-native governance-wrapped incident refinery: reduces alert noise 75% (4 alerts → 1 parent + 3 suppressed), ranks RCA, implements L3 auto-approved (audited) vs L4 human-approval-required workflows with RBAC, default-deny NetworkPolicies, OPA allowlist + approval-required policies, human gating via Approval Gateway, audit logging, and GLPI ITSM as system of record.

**Platform Engineering:**
- Architected Prism, a Kind-native (aiops-m5) control plane with 8 extraPortMappings, declarative k8s/ manifests, GitHub Actions CI that validates Kind cluster creation and manifest dry-run
- Built governance outer ring: RBAC least-privilege ServiceAccounts, default-deny NetworkPolicies with explicit allows, OPA policies (allowlist=[aiops-demo-nginx], L3 auto-approved per policy, L4 requires approval_id), Approval Gateway :8087 for human gating, audit metrics

**SRE / AIOps:**
- Built correlation engine (FastAPI + SQLite) grouping by `root_correlation_key`, achieving 4:1 noise suppression (1 parent + 3 child suppressed) with RCA ranking `vm_metrics_down` as root cause, metrics exposed for Grafana dashboards
- Implemented controlled autonomy: L3 safe container restart auto-approved per OPA policy but audited + reversible with approver `auto-policy-L3`, L4 high-risk infrastructure requires human approval via Cockpit/GLPI/API with approver identity + approval_id + token + allowlist + audit, GLPI as system of record

**Learning Approach:**
- Built ground-up from `k8s/kind-config.yaml` only, documenting Learn/Break/Build/Reflect in `docs/learning/` and `experiments/` - intentionally broke RBAC, NetworkPolicies, OPA to understand least privilege, zero trust, and human gating

---

## Governance

See [docs/GOVERNANCE.md](docs/GOVERNANCE.md)

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md)

---

## License

MIT - Learning project

---

## Author

Built as hands-on learning project for Platform Engineering / SRE / AIOps - ground-up, Kind-native, governance-wrapped
