#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
OUT="$REPO_ROOT/docs/proof/stripe_test_paymentintent_redacted.json"
mkdir -p "$(dirname "$OUT")"

if [[ -z "${STRIPE_SECRET_KEY:-}" ]]; then
  echo "STRIPE_SECRET_KEY not set; skipping Stripe test proof capture."
  exit 0
fi

export AQTC_DISABLE_HERMES_ENV=true
export AQTC_STRIPE_MODE=stripe_test
STATE_DIR="$(mktemp -d)"
export AQTC_STATE_DIR="$STATE_DIR"
export AQTC_REPO_ROOT="$REPO_ROOT"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:$PYTHONPATH}"
trap 'rm -rf "$STATE_DIR"' EXIT

python -m aqtc.cli demo --stripe-mode stripe_test --json >/dev/null

python - <<'PY'
import json
import os
from datetime import UTC, datetime
from pathlib import Path

repo = Path(os.environ["AQTC_REPO_ROOT"])
state = Path(os.environ["AQTC_STATE_DIR"])
ledger_path = state / "stripe_ledger.json"
out = repo / "docs" / "proof" / "stripe_test_paymentintent_redacted.json"

ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
earn = next(event for event in reversed(ledger) if event["kind"] == "earn")
redacted = {
    "mode": "stripe_test",
    "status": earn.get("status", "recorded"),
    "amount_usd": earn["amount_usd"],
    "currency": earn.get("metadata", {}).get("currency", "usd"),
    "external_id": earn.get("external_id"),
    "description": earn.get("description"),
    "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "note": "Redacted Stripe test PaymentIntent proof; no secrets stored.",
}
out.write_text(json.dumps(redacted, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(f"wrote {out}")
PY
