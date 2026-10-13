# Governance Outer Ring - PRISM

Everything surrounded by Governance & Security including human gating and approvals.

## Layers (Day 1-2)

1. RBAC (01-governance-rbac.yaml) - ServiceAccounts least-privilege
2. Secrets (04-secrets.yaml) - K8s Secret aiops-secrets, no .env in git
3. NetworkPolicies (02-governance-networkpolicies.yaml) - default-deny-all + explicit allows
4. OPA Policies (03-governance-opa-policies.yaml) - allowlist=[aiops-demo-nginx], L3 auto-approved low-risk, L4 requires approval_id
5. Approval Gateway :8087 (30-approval-gateway.yaml) - Human gating service
   - POST /approvals/request from correlator
   - L3 low-risk: auto-approved + audit + metrics
   - L4 high-risk: pending → human must POST /approvals/{id}/approve with X-Token + X-Approver identity
   - UI at :8087 with Approve/Deny buttons
6. Remediator requires X-Token + X-Approval-ID + X-Approver, validates approval_id via gateway, allowlist, audit
7. Audit: Prometheus metrics aiops_governance_approval_total{decision,risk_level,approver} + audit log
8. GLPI ITSM as system of record
