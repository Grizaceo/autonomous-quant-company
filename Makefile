.PHONY: install test demo report serve

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

demo:
	aqtc demo

report:
	aqtc report --out demo_report.md

serve:
	uvicorn aqtc.api.app:app --reload --host 127.0.0.1 --port 8010
