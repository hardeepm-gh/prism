#!/bin/bash
set -e
echo "=== PRISM - Day 0 - Folder Creation + GitHub Setup ==="
echo "Run this on local Mac in ~/ai-lab or wherever you want the lab"

# 1. Create structure
echo "Step 1: Creating folder structure..."
if [ -d "prism" ]; then
  echo "prism/ exists - removing for clean start? (y/n)"
  read -r ans
  if [ "$ans" = "y" ]; then
    rm -rf prism
  else
    echo "Keeping existing prism/, will merge"
  fi
fi

# Copy the Day 0 basics from this package
if [ -d "prism-day0-basics/prism" ]; then
  cp -r prism-day0-basics/prism .
else
  # If running from inside the extracted folder
  mkdir -p prism/k8s prism/scripts prism/services/approval-gateway/app prism/services/correlator/app prism/services/cockpit/app prism/services/remediator/app prism/docs/inventory prism/docs/daily-log prism/docs/architecture prism/data/demo prism/backups prism/.github/workflows
fi

chmod +x prism/scripts/*.sh

echo "Folder tree:"
find prism -type d | sort

# 2. Inventory
echo ""
echo "Step 2: Inventory local disk (what images/tools you have)..."
cd prism
./scripts/inventory-local.sh || echo "Inventory script needs docker/kind - continue anyway"
cd ..

# 3. Git init
echo ""
echo "Step 3: Git init + first commit..."
cd prism
if [ ! -d ".git" ]; then
  git init
  git add -A
  git commit -m "feat(day-0): basics - folder/sub-folder creation + kind-config + inventory script - ground-up start for PRISM"
  echo "Git init done - first commit created"
else
  echo "Git already initialized"
fi

# 4. GitHub repo creation
echo ""
echo "Step 4: GitHub repo creation..."
echo "Requires gh CLI authenticated. Checking..."
if ! command -v gh &> /dev/null; then
  echo "gh CLI not installed - install: brew install gh"
  echo "Manual GitHub creation:"
  echo "1. Go to github.com/new"
  echo "2. Create repo named 'prism' - public - no README"
  echo "3. Then run:"
  echo "   git remote add origin https://github.com/<you>/prism.git"
  echo "   git branch -M main"
  echo "   git push -u origin main"
else
  if gh auth status &> /dev/null; then
    echo "gh authenticated - creating repo prism..."
    gh repo create prism --public --source=. --push --description "Prism - Governance-wrapped incident refinery: Kind-native, 4:1 correlation, human gating" || echo "Repo may already exist, pushing..."
    git push -u origin main || git push
  else
    echo "gh not authenticated - run: gh auth login"
    echo "Then: gh repo create prism --public --source=. --push"
  fi
fi

echo ""
echo "=== Day 0 Done ==="
echo "Next:"
echo "1. Check GitHub: https://github.com/<you>/prism"
echo "2. Bootstrap Kind: cd prism && ./scripts/bootstrap-kind.sh"
echo "3. Health: ./scripts/kind-control.sh health"
echo "4. Daily log: docs/daily-log/$(date +%Y-%m-%d).md"
echo "5. Push: git add -A && git commit -m 'docs(day-0): daily log' && git push"
