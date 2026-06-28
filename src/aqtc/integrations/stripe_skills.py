from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal
import json


@dataclass(frozen=True)
class StripeLedgerEvent:
    kind: Literal["spend", "earn"]
    description: str
    amount_usd: float
    mode: str = "mock"


class StripeLedger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def append(self, event: StripeLedgerEvent) -> None:
        events = self.read()
        events.append(asdict(event))
        self.path.write_text(json.dumps(events, indent=2, sort_keys=True), encoding="utf-8")

    def read(self) -> list[dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def net(self) -> float:
        total = 0.0
        for e in self.read():
            total += e["amount_usd"] if e["kind"] == "earn" else -e["amount_usd"]
        return round(total, 2)


class MockStripeAdapter:
    def __init__(self, ledger: StripeLedger, *, mode: str = "mock", daily_budget_usd: float = 25.0):
        self.ledger = ledger
        self.mode = mode
        self.daily_budget_usd = daily_budget_usd

    def spend(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        spent = sum(e["amount_usd"] for e in self.ledger.read() if e["kind"] == "spend")
        if spent + amount_usd > self.daily_budget_usd:
            raise RuntimeError(f"budget exceeded: attempted {spent + amount_usd:.2f} > {self.daily_budget_usd:.2f}")
        event = StripeLedgerEvent(kind="spend", description=description, amount_usd=amount_usd, mode=self.mode)
        self.ledger.append(event)
        return event

    def earn(self, description: str, amount_usd: float) -> StripeLedgerEvent:
        event = StripeLedgerEvent(kind="earn", description=description, amount_usd=amount_usd, mode=self.mode)
        self.ledger.append(event)
        return event
