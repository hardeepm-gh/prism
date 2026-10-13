# PRISM Roadmap - 14 Days Ground-Up | GitHub Holds Everything

## Day 0 (Today) - Basics - Folder/Sub-folder + GitHub
- [x] Folder structure: k8s/, scripts/, services/, docs/, data/, backups/, .github/
- [x] k8s/kind-config.yaml (Kind cluster aiops-m5 + 8 extraPortMappings)
- [x] k8s/00-namespace.yaml (aiops-m5)
- [x] scripts/inventory-local.sh, bootstrap-kind.sh, kind-control.sh
- [x] .gitignore (secrets, data, backups ignored)
- [x] README.md with GitHub setup steps
- [ ] Run on M5: ./create-prism-structure.sh
- [ ] Run: ./scripts/inventory-local.sh → docs/inventory/LOCAL_INVENTORY.md
- [ ] Git init + gh repo create prism --public --source=. --push
- [ ] Commit: feat(day-0): basics - folder structure + kind control plane

## Day 1 - Governance RBAC + Secrets + NetworkPolicies (Outer Ring First)
- Create k8s/01-governance-rbac.yaml (ServiceAccounts, Roles, RoleBindings)
- Create k8s/04-secrets.yaml + scripts/gen-secrets.sh (K8s Secret aiops-secrets)
- Create k8s/02-governance-networkpolicies.yaml (default-deny-all + explicit allows)
- Apply: kubectl apply -f k8s/01-*, 04-*, 02-*
- Validate: kubectl get roles,rolebindings,networkpolicies,secrets -n aiops-m5
- Commit: feat(day-1): governance ring - RBAC + Secrets + NetworkPolicies

## Day 2 - OPA Policies + Approval Gateway Human Gating
- Create k8s/03-governance-opa-policies.yaml (allowlist=[aiops-demo-nginx], L3 auto-approved, L4 requires approval_id)
- Create services/approval-gateway/ FastAPI :8087 (POST /approvals/request, /approvals/{id}/approve, UI, metrics)
- Create k8s/30-approval-gateway.yaml NodePort 30088→8087
- Build: docker build -t prism-approval-gateway:latest + kind load
- Validate: curl :8087/healthz, test-governance (low-risk auto-approved, high-risk pending)
- Commit: feat(day-2): governance - OPA + Approval Gateway human gating :8087

## Day 3 - Prometheus + Rules
- Create k8s/10-prometheus-config.yaml (prometheus.yml + aiops-rules.yml DemoNGINXDown + 4 Claims alerts same root_correlation_key)
- Create k8s/11-prometheus.yaml NodePort 30083→9090
- Commit: feat(day-3): signal - prometheus + rules

## Day 4 - Alertmanager + Blackbox
- Create k8s/20-alertmanager.yaml (group_by root_correlation_key → webhook to correlator)
- Create k8s/40-blackbox.yaml NodePort 30087
- Commit: feat(day-4): signal - alertmanager grouping + blackbox

## Day 5 - Correlator Core Logic
- Create services/correlator/ FastAPI SQLite parent_incidents/child_alerts, /webhook/alertmanager 4:1 correlation, RCA ranking vm_metrics_down first
- Create k8s/31-correlator.yaml NodePort 30085
- Test: inject 4 alerts JSON → expect child_count 3, RCA business-app-vm / vm_metrics_down
- Commit: feat(day-5): intelligence - correlator 4:1 + RCA

## Day 6 - Correlator → Approval Gateway Integration
- Update correlator to call Approval Gateway POST /approvals/request after parent creation
- Add reset-correlation safe procedure
- Commit: feat(day-6): intelligence - correlator → approval gateway

## Day 7 - Cockpit Visual + Approve Button
- Create services/cockpit/ FastAPI HTML KPI cards, RCA table, Approve button
- Create k8s/32-cockpit.yaml NodePort 30080→8095
- Commit: feat(day-7): visualization - cockpit :8095

## Day 8 - Grafana Dashboards
- Create k8s/50-grafana.yaml datasources + dashboards provisioning + executive.json + rca.json + governance-audit.json
- NodePort 30081→3006
- Commit: feat(day-8): visualization - grafana dashboards

## Day 9 - Remediator Governance-Wrapped
- Create services/remediator/ FastAPI requires X-Token + X-Approval-ID + X-Approver, validates approval_id via gateway, allowlist, audit
- Create k8s/33-remediator.yaml ClusterIP
- Test DENY without approval_id, ALLOW with approved id
- Commit: feat(day-9): controlled act - remediator governance-wrapped

## Day 10 - GLPI + Demo NGINX
- Create k8s/60-glpi.yaml MariaDB + GLPI NodePort 30082, k8s/33-demo-nginx.yaml NodePort 30086
- Commit: feat(day-10): itsm + safe target

## Day 11 - Scenario 1 L3 Auto-Approved Closed-Loop
- Create scripts/run-prism-live-demo.sh Kind-native: scale nginx 0 → 45s → auto-approved in :8087 → scale 1 with approval_id + token → Grafana +1
- Commit: feat(day-11): scenario 1 L3 auto-approved

## Day 12 - Scenario 2 L4 Human Approval Required Multi-Alert
- Create scripts/run-claims-multialert-demo.sh 4 alerts same root key → 1 parent + 3 suppressed → pending in :8087 → human approves via Cockpit → remediator DENY for non-allowlisted per OPA (governance demo)
- Commit: feat(day-12): scenario 2 L4 human approval required

## Day 13 - Hardening PVC Backup Troubleshooting
- Add PVCs, backup-prism.sh, shutdown-prism.sh, docs/TROUBLESHOOTING.md, docs/VALIDATION.md
- Commit: feat(day-13): hardening

## Day 14 - Docs + Demo + Release v1.0.0
- docs/CLIENT_DEMO_GUIDE.md, docs/HLD.md, docs/LLD.md, final README, 2-min GIF, git tag v1.0.0-governed
- Commit: feat(day-14): release v1.0.0-governed

## GitHub Daily Workflow
git pull
./scripts/kind-control.sh health
Implement today's k8s/ file(s)
kubectl apply -f k8s/<today>.yaml
Create docs/daily-log/YYYY-MM-DD.md
git add -A && git commit -m "feat(day-N): ..." && git push
CI validates with Kind in GitHub Actions
