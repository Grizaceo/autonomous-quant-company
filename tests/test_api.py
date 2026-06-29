import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from aqtc.api import app as app_module


@pytest.fixture
def client(isolated_env, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(isolated_env))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    assert app_module.app is not None
    return TestClient(app_module.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_status(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert "config" in response.json()


def test_cycle_run(client):
    response = client.post("/cycle/run")
    assert response.status_code == 200
    data = response.json()
    assert data["stripe_net_usd"] == 17.0


def test_dashboard(client):
    client.post("/cycle/run")
    response = client.get("/")
    assert response.status_code == 200
    assert "Autonomous Quant Company" in response.text
    assert "$17.00" in response.text
