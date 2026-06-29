#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
git add -A
git commit -m "$1"
