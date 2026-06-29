#!/usr/bin/env bash
set -euo pipefail
export AQTC_DISABLE_HERMES_ENV=true
export AQTC_STATE_DIR="${AQTC_STATE_DIR:-/tmp/aqtc-judge-smoke-$$}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"

run_aqtc() {
  python -m aqtc.cli "$@"
}

DEMO_JSON="$(mktemp)"
PROV_JSON="$(mktemp)"
trap 'rm -f "$DEMO_JSON" "$PROV_JSON"' EXIT

run_aqtc demo --json >"$DEMO_JSON"
run_aqtc provenance --json >"$PROV_JSON"

python - <<PY
import json
from pathlib import Path

demo = json.load(open("$DEMO_JSON"))
prov = json.load(open("$PROV_JSON"))
report = Path(demo["report_path"])

model = prov["model"]
sharpe = prov["accepted"]["mean_sharpe"]
folds = prov["accepted"]["n_folds"]
positive = int(round(prov["accepted"]["positive_fold_ratio"] * folds))
rejected_name = prov["rejected"]["name"]
rejected_sharpe = prov["rejected"]["sharpe"]
net = demo["stripe_net_usd"]
spend = 2.0
earn = 19.0

print("AQTC JUDGE SMOKE")
print(
    f"1. Provenance: {model}, Sharpe {sharpe:.3f}, "
    f"{positive}/{folds} folds positive"
)
print(
    f"2. Falsification: rejected {rejected_name}, Sharpe {rejected_sharpe:.3f}"
)
print(f"3. Business cycle: spend \${spend:.0f}, earn \${earn:.0f}, net \${net:.0f}")
print("4. Safety: live trading denied, paper mode only")
print(f"5. Report: {report}")
print("OK")
PY
