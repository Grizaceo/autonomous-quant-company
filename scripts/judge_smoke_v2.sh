#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CREATED_STATE_DIR=""
if [[ -z "${AQTC_STATE_DIR:-}" ]]; then
  CREATED_STATE_DIR="$(mktemp -d)"
  export AQTC_STATE_DIR="$CREATED_STATE_DIR"
fi
trap '[[ -n "$CREATED_STATE_DIR" ]] && rm -rf "$CREATED_STATE_DIR"' EXIT

export AQTC_DISABLE_HERMES_ENV="${AQTC_DISABLE_HERMES_ENV:-true}"

run_aqtc() {
  if command -v aqtc >/dev/null 2>&1; then
    aqtc "$@"
  else
    python - "$@" <<'PY'
import sys
from aqtc.cli import main
raise SystemExit(main(sys.argv[1:]))
PY
  fi
}

section() {
  printf '\n\033[1;36m== %s ==\033[0m\n' "$1"
}

fail_missing() {
  echo "missing required artifact: $1" >&2
  exit 3
}

[[ -f data/demo/proof_manifest.generated.json ]] || fail_missing data/demo/proof_manifest.generated.json
[[ -f data/demo/walkforward_report.json ]] || fail_missing data/demo/walkforward_report.json
[[ -f data/demo/rejected_ensemble_2019.json ]] || fail_missing data/demo/rejected_ensemble_2019.json

section "secret scan"
scripts/pre_submission_secret_scan.sh

section "tests + coverage"
python -m pytest -q --cov=aqtc --cov-report=term-missing --cov-fail-under=90

section "lint"
ruff check .

section "typing"
mypy src tests

section "demo contracts"
run_aqtc demo --json >/tmp/aqtc_demo.json
run_aqtc provenance --json >/tmp/aqtc_provenance.json
run_aqtc status >/tmp/aqtc_status.json
python - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

paths = {
    "demo": Path("/tmp/aqtc_demo.json"),
    "provenance": Path("/tmp/aqtc_provenance.json"),
    "status": Path("/tmp/aqtc_status.json"),
}
loaded = {name: json.loads(path.read_text(encoding="utf-8")) for name, path in paths.items()}

demo = loaded["demo"]
assert demo["accepted_strategy"] is True
assert demo["rejected_bad_strategy"] is True
assert demo["stripe_net_usd"] >= 13.0
assert demo["portfolio_positions"] > 0
assert demo["nemotron_live"] is False

provenance = loaded["provenance"]
assert provenance["model"] == "HGAT+ES v4"
assert provenance["accepted"]["mean_sharpe"] >= 3.25
assert provenance["rejected"]["sharpe"] < 0

status = loaded["status"]
assert len(status["events"]) >= 9
assert status["report_path"]
print("demo JSON contracts ok")
PY

section "protected files"
if git rev-parse --verify main >/dev/null 2>&1; then
  touched="$(git diff --name-only main..HEAD | grep -E '^(README.md|docs/(JUDGE_ONE_PAGER|PITCH|ARCHITECTURE|WHY_HGAT_ES|ALPHA_PROVENANCE|EXTERNAL_SUBMISSION|MCP_SERVER|SUBMISSION_CHECKLIST|PAPER_DERIVED_VALIDATION_UPGRADES)\.md|scripts/judge_smoke\.sh|scripts/print_external_submission\.sh|src/aqtc/financial_core/harness/base\.py)$' || true)"
  if [[ -n "$touched" ]]; then
    echo "protected files touched:" >&2
    echo "$touched" >&2
    exit 1
  fi
fi

echo
printf '\033[1;32mAQTC judge smoke v2 PASS\033[0m\n'
