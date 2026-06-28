# MCP Server

AQTC exposes a FastMCP stdio server for Hermes or any MCP client.

## Tools

- `aqtc_status` — current policy, config, event log, ledger, and paper portfolio.
- `aqtc_run_cycle(reset: bool = true)` — run one safe paper business cycle.
- `aqtc_get_report` — return the generated customer report, creating one if needed.
- `aqtc_get_events` — return event log entries.

## Local validation

```bash
fastmcp inspect src/aqtc/mcp_server.py:mcp
fastmcp list src/aqtc/mcp_server.py --json
fastmcp call src/aqtc/mcp_server.py aqtc_run_cycle reset=true --json
```

## Hermes config snippet

```yaml
mcp_servers:
  aqtc:
    command: "aqtc-mcp"
    args: []
    timeout: 120
    connect_timeout: 60
```

After adding the server, restart Hermes or run `/reload-mcp`.
