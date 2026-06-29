from __future__ import annotations

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None
    HTMLResponse = None

from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent

if FastAPI is None:  # pragma: no cover
    app = None
else:
    app = FastAPI(title="Autonomous Quant Company")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/status")
    def status() -> dict:
        return AutonomousQuantCompanyAgent().status()

    @app.post("/cycle/run")
    def run_cycle() -> dict:
        return AutonomousQuantCompanyAgent().run_daily_cycle().to_dict()

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        agent = AutonomousQuantCompanyAgent()
        report_path = agent.config.state_dir / "customer_report.md"
        status_data = agent.status()
        ledger = status_data.get("ledger", [])
        net = sum(
            event["amount_usd"] if event["kind"] == "earn" else -event["amount_usd"]
            for event in ledger
        )
        report_html = "<p>No report yet. POST /cycle/run to generate one.</p>"
        if report_path.exists():
            report_html = f"<pre>{report_path.read_text(encoding='utf-8')}</pre>"
        events = status_data.get("events", [])
        last_event = events[-1] if events else {}
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Autonomous Quant Company</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 960px; }}
    .metric {{ display: inline-block; margin-right: 2rem; }}
    pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; }}
  </style>
</head>
<body>
  <h1>Autonomous Quant Company</h1>
  <p>Paper-trading business cycle dashboard (demo).</p>
  <div>
    <span class="metric"><strong>Net:</strong> ${net:.2f}</span>
    <span class="metric"><strong>Events:</strong> {len(events)}</span>
    <span class="metric"><strong>Stripe mode:</strong> {status_data["config"]["stripe_mode"]}</span>
    <span class="metric"><strong>Nemotron:</strong> {status_data["config"]["nvidia_mode"]}</span>
  </div>
  <h2>Last event</h2>
  <pre>{last_event}</pre>
  <h2>Customer report</h2>
  {report_html}
</body>
</html>"""
