from __future__ import annotations

from dataclasses import dataclass, field

from .signals import TradingSignal


@dataclass(frozen=True)
class RiskPolicy:
    max_gross_exposure: float = 4.0
    max_active_positions: int = 8
    max_single_position_weight: float = 2.0
    live_trading: bool = False


@dataclass(frozen=True)
class RiskAssessment:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    gross_exposure: float = 0.0
    active_positions: int = 0


class RiskGuard:
    def __init__(self, policy: RiskPolicy):
        self.policy = policy

    def assess(self, signal: TradingSignal, *, live_requested: bool = False) -> RiskAssessment:
        reasons: list[str] = []
        if live_requested and not self.policy.live_trading:
            reasons.append("live trading disabled; paper execution only")
        if signal.gross_exposure > self.policy.max_gross_exposure + 1e-9:
            reasons.append(
                f"gross exposure {signal.gross_exposure:.2f} > limit {self.policy.max_gross_exposure:.2f}"
            )
        if len(signal.positions) > self.policy.max_active_positions:
            reasons.append(
                f"active positions {len(signal.positions)} > limit {self.policy.max_active_positions}"
            )
        too_large = [p.ticker for p in signal.positions if abs(p.weight) > self.policy.max_single_position_weight]
        if too_large:
            reasons.append("single-position limit exceeded: " + ", ".join(too_large))
        return RiskAssessment(
            allowed=not reasons,
            reasons=reasons,
            gross_exposure=signal.gross_exposure,
            active_positions=len(signal.positions),
        )
