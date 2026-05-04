#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: scripts/checkpoint.sh \"Commit message\""
  exit 1
fi

git status
git diff --stat
git add .
git commit -m "$1"
