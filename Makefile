.PHONY: install test demo report serve

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

demo:
	aqtc demo

live-regime:
	aqtc regime --provider auto

mcp-inspect:
	fastmcp inspect src/aqtc/mcp_server.py:mcp

mcp-list:
	fastmcp list src/aqtc/mcp_server.py --json

mcp-call:
	fastmcp call src/aqtc/mcp_server.py aqtc_run_cycle reset=true --json

report:
	aqtc report --out demo_report.md

serve:
	uvicorn aqtc.api.app:app --reload --host 127.0.0.1 --port 8010
