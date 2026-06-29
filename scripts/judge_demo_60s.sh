#!/usr/bin/env bash
set -euo pipefail
export AQTC_DISABLE_HERMES_ENV=true
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
if [[ -f .venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

echo "=== AQTC judge demo (~60s recording) ==="
echo "[0:00] Provenance"
aqtc provenance | head -22
sleep 10
echo ""
echo "[0:20] Business cycle (DECISIONS block)"
aqtc demo
sleep 8
echo ""
echo "[0:45] Judge smoke"
bash scripts/judge_smoke.sh
echo ""
echo "[0:55] Close: From evolved alpha to invoice"
