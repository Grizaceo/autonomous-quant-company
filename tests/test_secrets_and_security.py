import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from aqtc.api import app as app_module
from aqtc.config import AQTCConfig
from aqtc.integrations.stripe_skills import MockStripeAdapter, StripeLedger, make_stripe_adapter
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR
from aqtc.secrets import get_secret


def test_get_secret_prefers_environment_over_file(tmp_path, monkeypatch):
    env_file = tmp_path / "secrets.env"
    env_file.write_text("AQTC_TEST_SECRET=from-file\n", encoding="utf-8")
    monkeypatch.setenv("AQTC_TEST_SECRET", "from-env")
    assert get_secret("AQTC_TEST_SECRET", env_file=env_file) == "from-env"


def test_get_secret_reads_key_value_file(tmp_path, monkeypatch):
    monkeypatch.delenv("AQTC_TEST_SECRET", raising=False)
    env_file = tmp_path / "secrets.env"
    env_file.write_text(
        "# comment\nexport AQTC_TEST_SECRET='quoted-file-value'\nIGNORED_LINE\n",
        encoding="utf-8",
    )
    assert get_secret("AQTC_TEST_SECRET", env_file=env_file) == "quoted-file-value"


def test_get_secret_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.delenv("AQTC_TEST_SECRET", raising=False)
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    assert get_secret("AQTC_TEST_SECRET", env_file=tmp_path / "missing.env") is None


def test_disable_hermes_env_blocks_host_env_fallback(tmp_path, monkeypatch):
    hermes_env = tmp_path / ".hermes" / ".env"
    hermes_env.parent.mkdir()
    hermes_env.write_text("AQTC_TEST_SECRET=from-hermes\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("AQTC_TEST_SECRET", raising=False)
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    assert get_secret("AQTC_TEST_SECRET") is None
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "false")
    assert get_secret("AQTC_TEST_SECRET") == "from-hermes"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    monkeypatch.delenv("AQTC_API_TOKEN", raising=False)
    assert app_module.app is not None
    return TestClient(app_module.app)


def test_api_cycle_requires_token_when_token_configured(client, monkeypatch):
    monkeypatch.setenv("AQTC_API_TOKEN", "secret-token")
    assert client.post("/cycle/run").status_code == 401
    assert client.post("/cycle/run", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert (
        client.post("/cycle/run", headers={"Authorization": "Bearer secret-token"}).status_code
        == 200
    )


def test_api_cycle_allows_without_token_only_when_unconfigured(client, monkeypatch):
    monkeypatch.delenv("AQTC_API_TOKEN", raising=False)
    response = client.post("/cycle/run")
    assert response.status_code == 200
    assert response.json()["accepted_strategy"] is True


def test_live_trading_request_is_blocked_by_policy(tmp_path):
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path, live_trading=True)
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    assert result.approval_status == "blocked"
    assert result.portfolio_positions == 0
    events = AutonomousQuantCompanyAgent(cfg).events.read()
    assert any(event["action"] == "skip_execution" for event in events)


def test_mock_mode_ignores_available_stripe_secret(tmp_path, monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_placeholder_not_live")
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = make_stripe_adapter(ledger, mode="mock", daily_budget_usd=25)
    assert isinstance(adapter, MockStripeAdapter)
    assert adapter.mode == "mock"
    event = adapter.earn("report", 19)
    assert event.status == "mock_recorded"
