#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export AQTC_DISABLE_HERMES_ENV=true
export AQTC_STATE_DIR="${AQTC_STATE_DIR:-/tmp/aqtc-judge-demo-$$}"
if [[ -f .venv/bin/activate ]]; then source .venv/bin/activate; fi
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
if [[ -f .env ]]; then set -a; source .env; set +a; fi

echo "=== Step 1/2: Provenance (HGAT+ES evidence) ==="
python -m aqtc.cli provenance
echo ""
echo "=== Step 2/2: Business cycle (stripe_test) ==="
python -m aqtc.cli demo --stripe-mode stripe_test --approve-spend
echo ""
echo "=== Judge demo complete (~60s) ==="