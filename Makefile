CLUSTER=aiops-m5
NAMESPACE=aiops-m5

.PHONY: folders inventory bootstrap up down health

folders:
	@echo "Creating folder structure..."
	@mkdir -p k8s scripts services/approval-gateway/app services/correlator/app services/cockpit/app services/remediator/app docs/inventory docs/daily-log docs/architecture data/demo backups .github/workflows .github/ISSUE_TEMPLATE
	@find . -type d -empty -exec touch {}/.gitkeep \;
	@find . -type d | sort

inventory:
	./scripts/inventory-local.sh

bootstrap:
	./scripts/bootstrap-kind.sh

up:
	./scripts/kind-control.sh up

down:
	./scripts/kind-control.sh down

health:
	./scripts/kind-control.sh health

# Day 1+ will add deploy targets
