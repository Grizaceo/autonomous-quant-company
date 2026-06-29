import pytest


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    return tmp_path
