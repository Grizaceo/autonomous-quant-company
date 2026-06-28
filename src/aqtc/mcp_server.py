"""Placeholder MCP entry point for P1.

P0 exposes CLI/API. P1 will wrap the same agent methods as MCP tools:
- aqtc_status
- aqtc_run_cycle
- aqtc_get_report
- aqtc_get_events
"""

from __future__ import annotations


def main() -> int:
    print("AQTC MCP server is planned for P1; use `aqtc demo` for P0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
