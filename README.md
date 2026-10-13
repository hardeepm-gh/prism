# PRISM - Governance-Wrapped Incident Refinery
> Kind-native, GitHub-native, ground-up build. Runbook v7 is REFERENCE ONLY.

## What is Prism?
- **Signal → Correlation → RCA → Human Gating → Controlled Act → Audit**
- 4 alerts with same `root_correlation_key` → 1 parent + 3 suppressed (75% noise reduction)
- L3 safe auto-approved per policy (audited) vs L4 high-risk requires human approval via Approval Gateway :8087
- Governance outer ring: RBAC + NetworkPolicies + OPA + Secrets + Audit + ITSM

## Day 0 - Basics (You are here)

### Folder Structure Created
```
prism/
├── k8s/
│   ├── kind-config.yaml          # Kind cluster aiops-m5 + extraPortMappings (8095,3006,8088,9090,9093,8089,8085,8087)
│   └── 00-namespace.yaml         # aiops-m5 namespace
├── scripts/
│   ├── inventory-local.sh        # Scan local disk: ~/ai-lab, docker images, backups
│   ├── bootstrap-kind.sh         # Day 1: kind create cluster
│   └── kind-control.sh           # Control panel: up/down/health/inventory
├── services/                     # Empty now, Day 2+ will build from scratch
│   ├── approval-gateway/app/.gitkeep
│   ├── correlator/app/.gitkeep
│   ├── cockpit/app/.gitkeep
│   └── remediator/app/.gitkeep
├── docs/
│   ├── inventory/                # LOCAL_INVENTORY.md
│   ├── daily-log/                # YYYY-MM-DD.md
│   ├── architecture/
│   └── ROADMAP.md
├── data/demo/.gitkeep
├── backups/.gitkeep              # gitignored
├── .github/workflows/
├── .gitignore
├── README.md
└── Makefile
```

### GitHub Setup (Day 0)

#### On your M5 Mac:

```bash
# 1. Create folder structure (run the script I gave you)
chmod +x create-prism-structure.sh
./create-prism-structure.sh
# Creates ./prism/

cd prism

# 2. Inventory local disk (what tools/images you already have)
chmod +x scripts/*.sh
./scripts/inventory-local.sh
cat docs/inventory/LOCAL_INVENTORY.md

# 3. Git init
git init
git add -A
git commit -m "feat(day-0): basics - folder structure + kind-config + inventory script - ground-up start"

# 4. Create GitHub repo (requires gh CLI)
# Option A: gh CLI (recommended)
gh auth login  # if not logged in
gh repo create prism --public --source=. --push
# Option B: manual
# - Go to github.com/new -> create repo "prism" -> public -> no README
# - Then:
# git remote add origin https://github.com/<you>/prism.git
# git branch -M main
# git push -u origin main

# 5. Verify GitHub
gh repo view --web
# or open https://github.com/<you>/prism

# 6. Bootstrap Kind control plane (Day 1 start)
./scripts/bootstrap-kind.sh
./scripts/kind-control.sh health
kubectl cluster-info --context kind-aiops-m5
kubectl get ns aiops-m5

# 7. Daily log
cat > docs/daily-log/2026-05-13.md <<EOF
# Day 0 - 2026-05-13 - Basics
## Done
- Folder/sub-folder creation: k8s/, scripts/, services/, docs/, data/, backups/, .github/
- kind-config.yaml + 00-namespace.yaml
- inventory-local.sh + bootstrap-kind.sh + kind-control.sh
- .gitignore (secrets, data, backups gitignored)
- GitHub repo prism created and pushed

## Inventory
- $(cat docs/inventory/LOCAL_INVENTORY.md | head -20)

## Next: Day 1 - Governance RBAC + NetworkPolicies + Secrets
EOF

git add -A
git commit -m "docs(day-0): daily log + inventory"
git push
```

#### GitHub Repo Settings (do once):

1. Go to repo Settings -> Branches -> Add rule: main requires PR? No, for this lab we push directly to main daily (ground-up lab)
2. Settings -> Actions -> General -> Workflow permissions: Read and write
3. Projects -> Create project board "Prism Build" with 14 issues (Day 1-14)

## Control Plane

Kind cluster `aiops-m5` is ONLY control panel:

```bash
./scripts/kind-control.sh health
# = kubectl cluster-info + kubectl get nodes + kubectl get ns + kubectl get pods -n aiops-m5

kubectl get pods -n aiops-m5 -o wide
kubectl logs -n aiops-m5 deployment/xxx -f
kubectl get svc -n aiops-m5
```

No Colima, no docker compose in v8 flow.

## URLs (after services deployed Day 3+)

- Cockpit: http://localhost:8095 (NodePort 30080)
- Approval Gateway (Human Gating): http://localhost:8087 (NodePort 30088)
- Grafana: http://localhost:3006 (NodePort 30081)
- GLPI: http://localhost:8088 (NodePort 30082)
- Prometheus: http://localhost:9090 (NodePort 30083)
- Alertmanager: http://localhost:9093 (NodePort 30084)
- Correlator: http://localhost:8089 (NodePort 30085)
- Demo NGINX: http://localhost:8085 (NodePort 30086)

## Roadmap

See docs/ROADMAP.md - 14 days ground-up, GitHub holds everything.

## Governance

See docs/GOVERNANCE.md - outer ring: RBAC + NetworkPolicies + OPA + Approval Gateway human gating + Audit.

## Principle

Runbook v7 is REFERENCE ONLY. We build from scratch in GitHub, using local disk images if present (docker images), but no copy-paste of v7 compose.
