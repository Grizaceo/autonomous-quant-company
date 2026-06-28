from __future__ import annotations

from pathlib import Path
from typing import Any

from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent

try:
    from fastmcp import FastMCP
except Exception:  # pragma: no cover - import guard for minimal installs
    FastMCP = None


def _agent() -> AutonomousQuantCompanyAgent:
    return AutonomousQuantCompanyAgent()


def aqtc_status() -> dict[str, Any]:
    """Return current AQTC state: policy, config, events, ledger, and paper portfolio."""
    return _agent().status()


def aqtc_run_cycle(reset: bool = True) -> dict[str, Any]:
    """Run one autonomous quant company business cycle in paper/safe mode."""
    return _agent().run_daily_cycle(reset=reset).to_dict()


def aqtc_get_report() -> dict[str, Any]:
    """Return the generated customer report, creating it via a cycle if missing."""
    agent = _agent()
    report = Path(agent.config.state_dir / "customer_report.md")
    if not report.exists():
        agent.run_daily_cycle(reset=True)
    return {"path": str(report), "content": report.read_text(encoding="utf-8")}


def aqtc_get_events() -> dict[str, Any]:
    """Return AQTC event log entries."""
    events = _agent().events.read()
    return {"count": len(events), "events": events}


if FastMCP is not None:
    mcp = FastMCP(name="Autonomous Quant Company")
    mcp.tool(aqtc_status)
    mcp.tool(aqtc_run_cycle)
    mcp.tool(aqtc_get_report)
    mcp.tool(aqtc_get_events)
else:  # pragma: no cover
    mcp = None


def main() -> int:
    if mcp is None:
        raise RuntimeError("fastmcp is required for the AQTC MCP server. Install with `pip install fastmcp`.")
    mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
