from unittest.mock import MagicMock, patch

import pytest

from aqtc.integrations.nvidia import OpenAICompatibleNemotronAdapter, make_nemotron_adapter
from aqtc.integrations.stripe_skills import StripeLedger, StripeTestModeAdapter


def test_mock_nemotron_summary():
    from aqtc.integrations.nvidia import MockNemotronAdapter

    summary = MockNemotronAdapter().summarize_market_regime({"x": 1})
    assert summary.live is False
    assert "paper mode" in summary.text


def test_auto_falls_back_to_mock_without_env(monkeypatch):
    from aqtc.integrations.nvidia import MockNemotronAdapter

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


def test_explicit_openrouter_without_key_returns_unavailable(monkeypatch, caplog):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    adapter = make_nemotron_adapter(
        mode="openrouter",
        openrouter_model="nvidia/test:free",
        nvidia_model="nvidia/test",
        opencode_zen_model="nvidia/test:free",
    )
    summary = adapter.summarize_market_regime({})
    assert summary.provider == "openrouter-unavailable"
    assert summary.live is False


@patch("aqtc.integrations.nvidia.get_secret", return_value="test-key")
def test_openrouter_live_success(mock_secret, monkeypatch):
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Live regime summary."))]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai = MagicMock()
    mock_openai.return_value = mock_client
    monkeypatch.setitem(__import__("sys").modules, "openai", MagicMock(OpenAI=mock_openai))

    adapter = OpenAICompatibleNemotronAdapter(
        provider="openrouter",
        model="nvidia/test",
        base_url="https://example.test/v1",
        api_key_name="OPENROUTER_API_KEY",
        explicit_mode=True,
    )
    summary = adapter.summarize_market_regime({"task": "test"})
    assert summary.live is True
    assert summary.provider == "openrouter"


@patch("aqtc.integrations.nvidia.get_secret", return_value="test-key")
def test_openrouter_api_error_falls_back(mock_secret, monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError("network down")
    mock_openai = MagicMock()
    mock_openai.return_value = mock_client
    monkeypatch.setitem(__import__("sys").modules, "openai", MagicMock(OpenAI=mock_openai))

    adapter = OpenAICompatibleNemotronAdapter(
        provider="openrouter",
        model="nvidia/test",
        base_url="https://example.test/v1",
        api_key_name="OPENROUTER_API_KEY",
    )
    summary = adapter.summarize_market_regime({})
    assert summary.provider == "openrouter-unavailable"
    assert "network down" in summary.text or "RuntimeError" in summary.text


@patch("aqtc.integrations.stripe_skills.get_secret", return_value="sk_test_abc")
def test_stripe_test_mode_earn_confirms_payment_intent(mock_secret, tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = StripeTestModeAdapter(ledger)
    payment_intent = {
        "id": "pi_test_123",
        "status": "succeeded",
        "object": "payment_intent",
        "livemode": False,
        "currency": "usd",
    }

    with patch.object(adapter, "_post_form", return_value=payment_intent) as post:
        event = adapter.earn("report", 19.0)

    post.assert_called_once()
    call_data = post.call_args[0][1]
    assert call_data["payment_method"] == "pm_card_visa"
    assert call_data["confirm"] == "true"
    assert event.status == "succeeded"
    assert event.metadata["collection"] == "succeeded"
    assert ledger.net() == 19.0


@patch("aqtc.integrations.stripe_skills.get_secret", return_value=None)
def test_stripe_test_mode_without_key_falls_back_to_mock(mock_secret, tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = StripeTestModeAdapter(ledger)
    event = adapter.earn("report", 19.0)
    assert event.mode == "stripe_test"
    assert event.status == "mock_recorded"


@patch("aqtc.integrations.stripe_skills.get_secret", return_value="sk_test_abc")
def test_stripe_test_mode_api_error(mock_secret, tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = StripeTestModeAdapter(ledger)
    with patch.object(adapter, "_post_form", side_effect=RuntimeError("Stripe API error 402")):
        with pytest.raises(RuntimeError, match="Stripe API error"):
            adapter.earn("report", 19.0)
