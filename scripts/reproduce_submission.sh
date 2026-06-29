#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
export AQTC_DISABLE_HERMES_ENV=true

if [[ -f "$REPO_ROOT/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/.venv/bin/activate"
else
  python -m pip install -e ".[dev,api,mcp,live]" -q
fi

export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
run_aqtc() { python -m aqtc.cli "$@"; }

echo "== install =="
python -m pip install -e ".[dev,api,mcp,live]" -q

echo "== pytest =="
python -m pytest -q --cov=aqtc --cov-report=term-missing

echo "== provenance =="
run_aqtc provenance --json | python -c "import json,sys; p=json.load(sys.stdin); assert p['model']=='HGAT+ES v4'"

echo "== judge smoke =="
bash scripts/judge_smoke.sh

echo "== smoke test =="
bash scripts/smoke_test.sh

echo "== stripe proof (optional) =="
bash scripts/capture_stripe_proof.sh

echo "== proof manifest =="
python scripts/generate_proof_manifest.py

echo "== demo + report =="
run_aqtc demo
run_aqtc report --run --out /tmp/aqtc-submission-report.md

echo ""
echo "Submission artifacts:"
echo "  Judge one-pager: docs/JUDGE_ONE_PAGER.md"
echo "  Proof manifest:  data/demo/proof_manifest.generated.json"
echo "  Customer report: .aqtc_state/customer_report.md"
echo "  Stripe proof:    docs/proof/stripe_test_paymentintent_redacted.json (if key was set)"
echo "  Demo video:      docs/demo-video/aqtc_demo.mp4"
