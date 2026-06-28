from aqtc.integrations.nvidia import MockNemotronAdapter, make_nemotron_adapter


def test_mock_nemotron_summary():
    summary = MockNemotronAdapter().summarize_market_regime({"x": 1})
    assert summary.live is False
    assert "paper mode" in summary.text


def test_auto_falls_back_to_mock_without_env(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("OPENCODE_ZEN_API_KEY", raising=False)
    monkeypatch.setenv("AQTC_SECRETS_FILE", "/tmp/aqtc-no-such-env-file")
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    adapter = make_nemotron_adapter(
        mode="auto",
        openrouter_model="nvidia/test:free",
        nvidia_model="nvidia/test",
        opencode_zen_model="nvidia/test:free",
    )
    assert isinstance(adapter, MockNemotronAdapter)
