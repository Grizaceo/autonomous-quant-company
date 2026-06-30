from unittest.mock import patch

import pytest

from aqtc.integrations.nvidia import MockNemotronAdapter, make_nemotron_adapter
from aqtc.integrations.stripe_skills import (
    MockStripeAdapter,
    StripeLedger,
    StripeTestModeAdapter,
    make_stripe_adapter,
)


def test_ledger_empty_net_zero(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    assert ledger.read() == []
    assert ledger.net() == 0.0


def test_ledger_spend_decreases_net(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    MockStripeAdapter(ledger).spend("data", 2.5)
    assert ledger.net() == -2.5


def test_ledger_earn_increases_net(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    MockStripeAdapter(ledger).earn("report", 19)
    assert ledger.net() == 19.0


def test_ledger_persists_across_instances(tmp_path):
    path = tmp_path / "ledger.json"
    MockStripeAdapter(StripeLedger(path)).earn("report", 19)
    assert StripeLedger(path).net() == 19.0


def test_mock_stripe_budget_guard_blocks_over_budget(tmp_path):
    adapter = MockStripeAdapter(StripeLedger(tmp_path / "ledger.json"), daily_budget_usd=5)
    adapter.spend("first", 4)
    with pytest.raises(RuntimeError, match="budget exceeded"):
        adapter.spend("second", 2)


def test_mock_stripe_budget_guard_allows_exact_budget(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = MockStripeAdapter(ledger, daily_budget_usd=5)
    event = adapter.spend("exact", 5)
    assert event.status == "mock_recorded"
    assert ledger.net() == -5


def test_adapter_factory_mock_returns_mock_adapter(tmp_path):
    adapter = make_stripe_adapter(
        StripeLedger(tmp_path / "ledger.json"), mode="mock", daily_budget_usd=25
    )
    assert isinstance(adapter, MockStripeAdapter)
    assert adapter.mode == "mock"


@patch("aqtc.integrations.stripe_skills.get_secret", return_value=None)
def test_adapter_factory_stripe_test_returns_stripe_test_adapter_without_calling_network(
    mock_secret, tmp_path
):
    adapter = make_stripe_adapter(
        StripeLedger(tmp_path / "ledger.json"), mode="stripe_test", daily_budget_usd=25
    )
    assert isinstance(adapter, StripeTestModeAdapter)
    assert adapter.available is False
    event = adapter.earn("report", 19)
    assert event.status == "mock_recorded"


def test_nemotron_auto_without_keys_returns_mock(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.delenv("OPENCODE_ZEN_API_KEY", raising=False)
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    adapter = make_nemotron_adapter(
        mode="auto",
        openrouter_model="nvidia/test:free",
        nvidia_model="nvidia/test",
        opencode_zen_model="nvidia/test:free",
    )
    assert isinstance(adapter, MockNemotronAdapter)


def test_explicit_openrouter_without_key_returns_unavailable_summary(monkeypatch):
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
