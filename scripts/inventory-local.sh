#!/bin/bash
set -e
mkdir -p docs/inventory
OUT="docs/inventory/LOCAL_INVENTORY.md"
echo "# PRISM Day 0 - Local Inventory - $(date)" | tee $OUT
echo "" | tee -a $OUT
echo "## 1. Where am I" | tee -a $OUT
pwd | tee -a $OUT
echo "" | tee -a $OUT
echo "## 2. Home folders" | tee -a $OUT
ls -1 ~ | head -100 | tee -a $OUT
echo "" | tee -a $OUT
echo "## 3. ~/ai-lab (your existing work)" | tee -a $OUT
ls -1 ~/ai-lab 2>/dev/null | tee -a $OUT || echo "No ~/ai-lab" | tee -a $OUT
echo "" | tee -a $OUT
echo "## 4. Backups (reference only, not to copy)" | tee -a $OUT
find ~/ai-lab -name "*baseline*.tar.gz" 2>/dev/null | head -10 | tee -a $OUT
ls -lh ~/ai-lab/aiops-portable-lab/backups/ 2>/dev/null | tail -10 | tee -a $OUT || echo "No backups folder" | tee -a $OUT
echo "" | tee -a $OUT
echo "## 5. Docker images already on local disk (to reuse)" | tee -a $OUT
docker images --format "{{.Repository}}:{{.Tag}} ({{.Size}})" 2>/dev/null | sort | tee -a $OUT || echo "docker not running - start Docker Desktop or Colima" | tee -a $OUT
echo "" | tee -a $OUT
echo "## 6. Tools" | tee -a $OUT
echo "kind: $(kind version 2>&1)" | tee -a $OUT
echo "kubectl: $(kubectl version --client 2>&1 | head -1)" | tee -a $OUT
echo "docker: $(docker version --format '{{.Client.Version}}' 2>&1 || echo 'not running')" | tee -a $OUT
echo "gh: $(gh --version 2>&1 | head -1 || echo 'gh not installed')" | tee -a $OUT
echo "" | tee -a $OUT
echo "Saved to $OUT - commit this file"
