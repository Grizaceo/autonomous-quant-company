from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketRegimeSummary:
    provider: str
    text: str


class MockNemotronAdapter:
    def summarize_market_regime(self) -> MarketRegimeSummary:
        return MarketRegimeSummary(
            provider="mock-nemotron",
            text=(
                "Demo regime: operate in paper mode, prefer validated HGAT+ES v4, "
                "reject strategies with poor out-of-sample drawdown."
            ),
        )
