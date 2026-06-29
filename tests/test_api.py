import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from aqtc.api import app as app_module


@pytest.fixture
def client(isolated_env, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(isolated_env))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    monkeypatch.delenv("AQTC_API_TOKEN", raising=False)
    assert app_module.app is not None
    return TestClient(app_module.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "config" in data
    assert "provenance" in data


def test_provenance(client):
    response = client.get("/provenance")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "HGAT+ES v4"
    assert data["accepted"]["mean_sharpe"] == pytest.approx(3.255, abs=0.01)


def test_cycle_run(client):
    response = client.post("/cycle/run")
    assert response.status_code == 200
    data = response.json()
    assert data["stripe_net_usd"] == 17.0
    assert data["rejected_candidate_sharpe"] == pytest.approx(-0.544, abs=0.01)


def test_cycle_run_requires_token_when_configured(client, monkeypatch):
    monkeypatch.setenv("AQTC_API_TOKEN", "secret-token")
    response = client.post("/cycle/run")
    assert response.status_code == 401
    response = client.post("/cycle/run", headers={"Authorization": "Bearer secret-token"})
    assert response.status_code == 200


def test_dashboard(client):
    client.post("/cycle/run")
    response = client.get("/")
    assert response.status_code == 200
    text = response.text
    assert "Autonomous Quant Company" in text
    assert "HGAT+ES" in text
    assert "Sharpe" in text
    assert "3.255" in text
    assert "Bad strategy rejected" in text
    assert "-0.544" in text
    assert "Net" in text
    assert "$17.00" in text
    assert "Alpha origin" in text
