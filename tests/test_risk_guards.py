from aqtc.financial_core.risk import RiskGuard, RiskPolicy
from aqtc.financial_core.signals import TradingSignal, PositionSignal, cap_signal


def sample_signal(gross=6.0):
    return TradingSignal(
        generated_at="now",
        model="test",
        positions=[PositionSignal("A", gross / 2, 1.0, 1.0), PositionSignal("B", gross / 2, 1.0, 1.0)],
        gross_exposure=gross,
        net_exposure=gross,
    )


def test_risk_blocks_excess_gross():
    assessment = RiskGuard(RiskPolicy(max_gross_exposure=4.0)).assess(sample_signal(6.0))
    assert assessment.allowed is False
    assert "gross exposure" in assessment.reasons[0]


def test_cap_signal_allows_policy():
    capped = cap_signal(sample_signal(6.0), max_gross=4.0)
    assessment = RiskGuard(RiskPolicy(max_gross_exposure=4.0)).assess(capped)
    assert assessment.allowed is True
    assert capped.gross_exposure == 4.0


def test_live_trading_disabled_by_default():
    assessment = RiskGuard(RiskPolicy(live_trading=False)).assess(sample_signal(1.0), live_requested=True)
    assert assessment.allowed is False
    assert "live trading disabled" in assessment.reasons[0]
