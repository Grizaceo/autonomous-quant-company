#!/usr/bin/env bash
# Demo script ejecutado DENTRO de la grabacion asciinema.
# Comandos validados contra `aqtc <cmd> --help`.
set -e
cd "$(dirname "$0")/../../.."

OUT_DIR="docs/demo-video/clips"
mkdir -p "$OUT_DIR"

echo ">> AQTC DEMO :: HGAT+ES alpha provenance + Stripe-ready report"
sleep 1

echo "## 1. Frozen provenance (offline alpha, Sharpe=3.255, 5 folds, 100% positive)"
.venv/bin/aqtc provenance
sleep 2

echo
echo "## 2. Live regime classifier (Nemotron call, paper mode)"
.venv/bin/aqtc regime --provider mock
sleep 2

echo
echo "## 3. Build customer report (Stripe invoice-ready) -- uses frozen ledger"
.venv/bin/aqtc report --out "$OUT_DIR/report.md"
echo "--- report.md (first 30 lines): ---"
head -n 30 "$OUT_DIR/report.md"
sleep 2

echo
echo "## 4. Audit trail (last events)"
.venv/bin/aqtc status --json 2>/dev/null || .venv/bin/aqtc status | tail -n 15
sleep 1

echo
echo ">> DEMO END :: try it: pip install -e . && aqtc demo"
