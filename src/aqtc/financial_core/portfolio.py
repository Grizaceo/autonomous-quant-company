from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .signals import TradingSignal


@dataclass
class PortfolioState:
    cash_usd: float = 100_000.0
    positions: dict[str, float] = field(default_factory=dict)
    mode: str = "paper"

    def to_dict(self) -> dict:
        return asdict(self)


class MockBroker:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> PortfolioState:
        if not self.state_path.exists():
            return PortfolioState()
        raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        return PortfolioState(**raw)

    def save(self, state: PortfolioState) -> None:
        self.state_path.write_text(
            json.dumps(state.to_dict(), indent=2, sort_keys=True), encoding="utf-8"
        )

    def rebalance(self, signal: TradingSignal) -> PortfolioState:
        state = self.load()
        state.positions = {p.ticker: p.weight for p in signal.positions}
        self.save(state)
        return state
