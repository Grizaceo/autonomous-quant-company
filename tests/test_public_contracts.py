import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from aqtc import mcp_server
from aqtc.api import app as app_module
from aqtc.cli import main
from aqtc.config import AQTCConfig
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR


def _assert_keys(data: dict, keys: set[str]) -> None:
    assert keys.issubset(data.keys())


def test_cli_demo_json_contract_keys(isolated_env, capsys):
    assert main(["demo", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    _assert_keys(
        data,
        {
            "accepted_strategy",
            "rejected_bad_strategy",
            "approval_status",
            "portfolio_positions",
            "gross_exposure",
            "stripe_net_usd",
            "report_path",
            "event_count",
            "nemotron_provider",
            "nemotron_live",
            "stripe_mode",
            "accepted_candidate_sharpe",
            "rejected_candidate_sharpe",
            "rejected_candidate_max_drawdown",
            "rejection_reason",
        },
    )


def test_cli_provenance_json_contract_keys(isolated_env, capsys):
    assert main(["provenance", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    _assert_keys(
        data,
        {
            "engine",
            "model",
            "algorithm",
            "genotype_dim",
            "production_config",
            "accepted",
            "rejected",
        },
    )
    _assert_keys(
        data["accepted"], {"mean_sharpe", "n_folds", "positive_fold_ratio", "mean_max_drawdown"}
    )
    _assert_keys(data["rejected"], {"name", "sharpe", "max_drawdown", "reason"})


def test_cli_status_json_contract_keys(isolated_env, capsys):
    main(["demo", "--json"])
    capsys.readouterr()
    assert main(["status"]) == 0
    data = json.loads(capsys.readouterr().out)
    _assert_keys(
        data, {"events", "ledger", "portfolio", "policy", "provenance", "config", "report_path"}
    )


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    monkeypatch.delenv("AQTC_API_TOKEN", raising=False)
    assert app_module.app is not None
    return TestClient(app_module.app)


def test_api_status_contract_keys(client):
    data = client.get("/status").json()
    _assert_keys(
        data, {"events", "ledger", "portfolio", "policy", "provenance", "config", "report_path"}
    )


def test_api_provenance_contract_keys(client):
    data = client.get("/provenance").json()
    _assert_keys(
        data,
        {
            "engine",
            "model",
            "algorithm",
            "genotype_dim",
            "production_config",
            "accepted",
            "rejected",
        },
    )


def test_api_run_cycle_contract_keys(client):
    data = client.post("/cycle/run").json()
    _assert_keys(
        data,
        {
            "accepted_strategy",
            "rejected_bad_strategy",
            "stripe_net_usd",
            "report_path",
            "event_count",
        },
    )


@pytest.fixture
def isolated_mcp(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    mcp_server.reset_agent()
    mcp_server._agent_instance = AutonomousQuantCompanyAgent(
        AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    )
    yield
    mcp_server.reset_agent()


def test_mcp_status_contract_keys(isolated_mcp):
    data = mcp_server.aqtc_status()
    _assert_keys(
        data, {"events", "ledger", "portfolio", "policy", "provenance", "config", "report_path"}
    )


def test_mcp_run_cycle_contract_keys(isolated_mcp):
    data = mcp_server.aqtc_run_cycle(reset=True)
    _assert_keys(
        data,
        {
            "accepted_strategy",
            "rejected_bad_strategy",
            "stripe_net_usd",
            "report_path",
            "event_count",
        },
    )


def test_mcp_get_report_contract_keys(isolated_mcp):
    data = mcp_server.aqtc_get_report(run=True)
    _assert_keys(data, {"exists", "path", "content"})
    assert data["exists"] is True


def test_mcp_get_events_contract_keys(isolated_mcp):
    mcp_server.aqtc_run_cycle(reset=True)
    data = mcp_server.aqtc_get_events()
    _assert_keys(data, {"count", "events"})
    assert data["count"] == len(data["events"])
