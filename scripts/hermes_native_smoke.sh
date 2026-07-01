#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v hermes >/dev/null 2>&1; then
  if hermes mcp list 2>/dev/null | grep -qE '(^|[[:space:]])aqtc([[:space:]]|$)'; then
    echo "hermes mcp: aqtc enabled"
  else
    echo "hermes mcp: aqtc not currently enabled in this Hermes profile"
    echo "hint: hermes mcp add aqtc --command aqtc-mcp && hermes mcp test aqtc"
  fi
else
  echo "hermes CLI not found; skipping live Hermes profile check"
fi

state_dir="$(mktemp -d)"
trap 'rm -rf "$state_dir"' EXIT

AQTC_STATE_DIR="$state_dir" AQTC_DISABLE_HERMES_ENV=true python - <<'PY'
from aqtc import mcp_server

mcp_server.reset_agent()
status = mcp_server.aqtc_status()
provenance = mcp_server.aqtc_get_provenance()
result = mcp_server.aqtc_run_cycle(reset=True)
events = mcp_server.aqtc_get_events()["events"]
report = mcp_server.aqtc_get_report(run=False)

actions = [event["action"] for event in events]
assert status["policy"]["live_trading"] is False
assert provenance["accepted"]["mean_sharpe"] > 3.0
assert result["strategy_integrity_status"] == "verified"
assert result["strategy_integrity_checked"] == 5
assert "verify_strategy_integrity" in actions
assert report["exists"] is True
assert "Strategy artifact integrity" in report["content"]
print("aqtc MCP tool surface: ok")
print(f"events: {len(actions)} ({', '.join(actions)})")
PY
