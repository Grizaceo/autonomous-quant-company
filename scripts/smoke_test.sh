#!/usr/bin/env bash
set -euo pipefail
export AQTC_DISABLE_HERMES_ENV=true
export AQTC_STATE_DIR="${AQTC_STATE_DIR:-/tmp/aqtc-smoke-$$}"
python -m pytest -q --cov=aqtc --cov-report=term-missing
aqtc demo --json >/tmp/aqtc-demo.json
python - <<'PY'
import json
x=json.load(open('/tmp/aqtc-demo.json'))
assert x['accepted_strategy'] is True
assert x['rejected_bad_strategy'] is True
assert x['approval_status'] == 'approved'
assert x['stripe_net_usd'] == 17.0
assert x['nemotron_provider'] in {'mock-nemotron', 'openrouter', 'nvidia-nim', 'opencode-zen', 'openrouter-unavailable', 'nvidia-nim-unavailable', 'opencode-zen-unavailable'}
assert x['stripe_mode'] in {'mock', 'stripe_test'}
print('smoke ok')
PY
