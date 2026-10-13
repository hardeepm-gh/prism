#!/bin/bash
set -e
echo "=== PRISM Day 0 - Folder/Sub-folder Creation (Basics) ==="
echo "Creating in current directory: $(pwd)"

# Root
mkdir -p prism
cd prism

# Core structure - ground-up, Kind control plane only
mkdir -p k8s
mkdir -p scripts
mkdir -p services/approval-gateway/app
mkdir -p services/correlator/app
mkdir -p services/cockpit/app
mkdir -p services/remediator/app
mkdir -p docs/inventory
mkdir -p docs/daily-log
mkdir -p docs/architecture
mkdir -p data/demo
mkdir -p backups
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE

# Create .gitkeep to keep empty folders in Git
find . -type d -empty -exec touch {}/.gitkeep \;

echo "Folder tree created:"
find . -type d | sort | head -50

echo ""
echo "Structure:"
echo "prism/"
echo "├── k8s/                          # Kind control plane + all K8s manifests (ground-up)"
echo "│   ├── kind-config.yaml          # Day 0 - Kind cluster definition"
echo "│   └── 00-namespace.yaml         # Day 0 - aiops-m5 namespace"
echo "├── scripts/                      # Control scripts"
echo "│   ├── inventory-local.sh        # Day 0 - scan local disk/tools/images"
echo "│   ├── bootstrap-kind.sh         # Day 1 - kind create cluster"
echo "│   └── kind-control.sh           # Control panel: up/down/health"
echo "├── services/                     # Custom images built from scratch"
echo "│   ├── approval-gateway/         # Day 2 - Human gating :8087"
echo "│   ├── correlator/               # Day 5 - Parent/child correlation"
echo "│   ├── cockpit/                  # Day 7 - Visual + Approve button"
echo "│   └── remediator/               # Day 9 - Governance-wrapped"
echo "├── docs/"
echo "│   ├── inventory/                # LOCAL_INVENTORY.md (local inventory scan)"
echo "│   ├── daily-log/                # YYYY-MM-DD.md daily updates"
echo "│   ├── architecture/             # Diagrams"
echo "│   ├── GOVERNANCE.md             # Governance outer ring"
echo "│   └── ROADMAP.md                # 14-day plan"
echo "├── data/demo/                    # current_exercise.json"
echo "├── backups/                      # gitignored - local backups"
echo "├── .github/workflows/            # CI validates Kind in GitHub Actions"
echo "├── .gitignore"
echo "├── README.md"
echo "└── Makefile"

cd ..
echo ""
echo "Done. Next: GitHub setup"
