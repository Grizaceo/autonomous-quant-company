from __future__ import annotations

import html
import os

from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent

try:
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None
    Header = None
    HTTPException = None
    HTMLResponse = None


def _check_api_token(authorization: str | None = Header(default=None)) -> None:
    token = os.getenv("AQTC_API_TOKEN")
    if not token:
        return
    if authorization != f"Bearer {token}":
        raise HTTPException(status_code=401, detail="invalid or missing API token")


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

    @app.get("/provenance")
    def provenance() -> dict:
        return AutonomousQuantCompanyAgent().get_provenance()

    @app.post("/cycle/run")
    def run_cycle(authorization: str | None = Header(default=None)) -> dict:
        _check_api_token(authorization)
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
        spend = sum(event["amount_usd"] for event in ledger if event["kind"] == "spend")
        earn = sum(event["amount_usd"] for event in ledger if event["kind"] == "earn")
        report_text = ""
        report_html = "<p>No report yet. POST /cycle/run to generate one.</p>"
        if report_path.exists():
            report_text = report_path.read_text(encoding="utf-8")
            report_html = f"<pre>{html.escape(report_text)}</pre>"

        events = status_data.get("events", [])
        last_event = events[-1] if events else {}
        last_event_html = html.escape(str(last_event))

        prov = status_data.get("provenance", agent.get_provenance())
        accepted = prov.get("accepted", {})
        rejected = prov.get("rejected", {})
        policy = status_data.get("policy", {})

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Autonomous Quant Company</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 960px; line-height: 1.5; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin: 1.5rem 0; }}
    .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 1rem; background: #fafafa; }}
    .card h2 {{ margin: 0 0 0.5rem; font-size: 1rem; color: #333; }}
    .metric {{ display: block; margin: 0.25rem 0; }}
    pre {{ background: #f4f4f4; padding: 1rem; overflow-x: auto; font-size: 0.85rem; }}
  </style>
</head>
<body>
  <h1>Autonomous Quant Company</h1>
  <p>Paper-trading business cycle dashboard (demo). <em>From evolved alpha to invoice.</em></p>
  <div class="cards">
    <div class="card">
      <h2>Alpha origin</h2>
      <span class="metric"><strong>Model:</strong> {html.escape(str(prov.get("model", "")))}</span>
      <span class="metric"><strong>Sharpe:</strong> {accepted.get("mean_sharpe", 0):.3f}</span>
      <span class="metric"><strong>Folds:</strong> {accepted.get("n_folds", 0)} ({accepted.get("positive_fold_ratio", 0):.0%} positive)</span>
      <span class="metric"><strong>MaxDD:</strong> {accepted.get("mean_max_drawdown", 0):.3f}</span>
    </div>
    <div class="card">
      <h2>Bad strategy rejected</h2>
      <span class="metric"><strong>Name:</strong> {html.escape(str(rejected.get("name", "")))}</span>
      <span class="metric"><strong>Sharpe:</strong> {rejected.get("sharpe", 0):.3f}</span>
      <span class="metric"><strong>MaxDD:</strong> {rejected.get("max_drawdown", 0):.3f}</span>
      <span class="metric"><strong>Reason:</strong> {html.escape(str(rejected.get("reason", "")))}</span>
    </div>
    <div class="card">
      <h2>Policy gate</h2>
      <span class="metric"><strong>ID:</strong> {html.escape(str(policy.get("policy_id", "")))}</span>
      <span class="metric"><strong>Daily budget:</strong> ${policy.get("daily_budget_usd", 0):.2f}</span>
      <span class="metric"><strong>Max gross:</strong> {policy.get("max_gross_exposure", 0)}</span>
      <span class="metric"><strong>Live trading:</strong> {policy.get("live_trading", False)}</span>
    </div>
    <div class="card">
      <h2>Invoice / revenue</h2>
      <span class="metric"><strong>Spend:</strong> ${spend:.2f}</span>
      <span class="metric"><strong>Earn:</strong> ${earn:.2f}</span>
      <span class="metric"><strong>Net:</strong> ${net:.2f}</span>
      <span class="metric"><strong>Stripe mode:</strong> {html.escape(str(status_data["config"]["stripe_mode"]))}</span>
    </div>
  </div>
  <h2>Last event</h2>
  <pre>{last_event_html}</pre>
  <h2>Report preview</h2>
  {report_html}
</body>
</html>"""
