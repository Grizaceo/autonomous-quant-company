#!/usr/bin/env bash
set -euo pipefail
python -m pytest -q
aqtc demo --json >/tmp/aqtc-demo.json
python - <<'PY'
import json
x=json.load(open('/tmp/aqtc-demo.json'))
assert x['accepted_strategy'] is True
assert x['rejected_bad_strategy'] is True
assert x['approval_status'] == 'approved'
assert x['nemotron_provider'] in {'mock-nemotron', 'openrouter', 'nvidia-nim', 'opencode-zen'}
assert x['stripe_mode'] in {'mock', 'stripe_test'}
print('smoke ok')
PY
