#!/usr/bin/env bash
set -euo pipefail
export AQTC_DISABLE_HERMES_ENV=true
export AQTC_STATE_DIR="${AQTC_STATE_DIR:-/tmp/aqtc-smoke-$$}"
python -m pytest -q --cov=aqtc --cov-report=term-missing
aqtc demo --json >/tmp/aqtc-demo.json
aqtc provenance --json >/tmp/aqtc-provenance.json
python - <<'PY'
import json
x=json.load(open('/tmp/aqtc-demo.json'))
assert x['accepted_strategy'] is True
assert x['rejected_bad_strategy'] is True
assert x['approval_status'] == 'approved'
assert x['stripe_net_usd'] == 17.0
assert abs(x['accepted_candidate_sharpe'] - 3.255) < 0.01
assert x['rejected_candidate_sharpe'] is not None and abs(x['rejected_candidate_sharpe'] + 0.544) < 0.01
assert x['nemotron_provider'] in {'mock-nemotron', 'openrouter', 'nvidia-nim', 'opencode-zen', 'openrouter-unavailable', 'nvidia-nim-unavailable', 'opencode-zen-unavailable'}
assert x['stripe_mode'] in {'mock', 'stripe_test'}
p=json.load(open('/tmp/aqtc-provenance.json'))
assert p['model'] == 'HGAT+ES v4'
assert abs(p['accepted']['mean_sharpe'] - 3.255) < 0.01
print('smoke ok')
PY
