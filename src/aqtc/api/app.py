from __future__ import annotations

try:
    from fastapi import FastAPI
except Exception:  # pragma: no cover - optional dependency
    FastAPI = None

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
