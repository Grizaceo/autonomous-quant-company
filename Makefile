.PHONY: install install-all test demo report serve lint format typecheck smoke

install:
	python -m pip install -e ".[dev]"

install-all:
	python -m pip install -e ".[dev,api,mcp,live]"

test:
	python -m pytest -q --cov=aqtc --cov-report=term-missing

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
	aqtc report --run --out demo_report.md

serve:
	uvicorn aqtc.api.app:app --reload --host 127.0.0.1 --port 8010

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src/aqtc

smoke:
	bash scripts/smoke_test.sh
