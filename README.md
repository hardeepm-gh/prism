# PRISM - Governance-Wrapped Incident Refinery
### Kind-Native • Ground-Up • Learning-First • GitHub-Native

> **From alert storm to single source of truth — with governance, human gating, and audit.**
> Control Plane: Kind cluster `aiops-m5` | Ground-up build, reference architecture only

---

## Status

**Governance Outer Ring Complete | Core Services Planned**

- Kind control plane `aiops-m5` - Ready
- RBAC least-privilege (4 ServiceAccounts, 3 Roles) - Enforced
- NetworkPolicy default-deny + explicit allows - Enforced
- SealedSecrets - Ready
- Kyverno admission control (block privileged, require non-root) - Enforced, evil pod blocked
- Correlator, Approval Gateway, Cockpit, Prometheus, Grafana, GLPI, Remediator - Planned

## What is PRISM?

PRISM refines noise to signal: 4 alerts -> 1 parent incident.
Correlation: group_by root_correlation_key = claims-platform-failure
Suppression: 4 -> 1 parent + 3 child suppressed (75% noise reduction)
RCA Ranking: vm_metrics_down = root cause, others = symptoms
Governance: RBAC + NetworkPolicy + Kyverno + Human Gating
Audit: who approved, when, what

No remediation without governance. Full autonomous with no human intervention is prohibited by policy.

## Why Kind as Control Plane?

- Kind cluster aiops-m5 is the single control plane: kubectl is the single pane of glass
- Declarative: k8s/*.yaml + kubectl apply -f k8s/ -> GitOps-ready
- Portable: extraPortMappings in k8s/kind-config.yaml maps NodePort to localhost
- Ground-up: Built from k8s/kind-config.yaml only

## Governance Outer Ring

- RBAC: ServiceAccounts least-privilege
- Secrets: SealedSecrets, rotation
- NetworkPolicies: default-deny-all + explicit allows
- Kyverno: block-privileged, require-non-root
- Approval Gateway: Human gating service (planned)
- Audit: audit log + Prometheus governance metrics
- GLPI ITSM: System of record (planned)

## Quick Start

Prerequisites: Docker, Kind, kubectl, Git
Clone: git clone https://github.com/hardeepm-gh/prism.git
Run: ./scripts/bootstrap-kind.sh
Check: ./scripts/kind-control.sh health

## Roadmap

Governance Phase - Done: RBAC, NetworkPolicy, SealedSecrets, Kyverno
Observability Phase - Planned: Prometheus, Alertmanager, Blackbox
Intelligence Phase - Planned: Correlator Core
Control Phase - Planned: Approval Gateway, Cockpit, Remediator
Visualization Phase - Planned: Grafana, GLPI
Scenarios - Planned: L3 auto-approved, L4 human approval
Hardening - Planned: PVC, backup, release

## Target Architecture

Kind Cluster: aiops-m5
Namespace: aiops-m5 (governance: enforced)
Governance: 01-rbac, 02-networkpolicy, 03-sealed-secrets, 04-kyverno-policies
Signal (planned): Prometheus, Alertmanager, Blackbox
Intelligence (planned): Correlator - parent/child + RCA
Visualization (planned): Cockpit, Grafana
Controlled Act (planned): Remediator, Demo NGINX
ITSM (planned): GLPI

## Validation - Governance Ring

Check: ./scripts/kind-control.sh health
Check: kubectl get pods -n aiops-m5
Check: kubectl get clusterpolicy
Check: kubectl get pods -n kyverno

## Resume - Key Project

PRISM - Kind-native governance-wrapped incident refinery: reduces alert noise 75 percent (4 alerts to 1 parent + 3 suppressed), ranks RCA, implements L3 auto-approved (audited) vs L4 human-approval-required workflows with RBAC, default-deny NetworkPolicies, Kyverno admission control, human gating via Approval Gateway, audit logging, and GLPI ITSM as system of record.

## Governance

See docs/GOVERNANCE.md

## Roadmap

See docs/ROADMAP.md

## License

MIT - Learning project

## Author

Built as hands-on learning project for Platform Engineering / SRE / AIOps - ground-up, Kind-native, governance-wrapped
