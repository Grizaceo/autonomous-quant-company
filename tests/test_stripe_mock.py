import pytest

from aqtc.integrations.stripe_skills import MockStripeAdapter, StripeLedger


def test_mock_stripe_ledger_net(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    stripe = MockStripeAdapter(ledger, daily_budget_usd=5)
    stripe.spend("data", 2)
    stripe.earn("report", 19)
    assert ledger.net() == 17


def test_mock_stripe_budget_guard(tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    stripe = MockStripeAdapter(ledger, daily_budget_usd=1)
    with pytest.raises(RuntimeError):
        stripe.spend("too much", 2)
