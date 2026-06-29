#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
msg="$1"
shift
if [ "$#" -gt 0 ]; then
  git add "$@"
else
  git add -A
fi
git commit -m "$msg"
