from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PositionSignal:
    ticker: str
    weight: float
    last_close: float
    position_value_per_100k: float


@dataclass(frozen=True)
class TradingSignal:
    generated_at: str
    model: str
    positions: list[PositionSignal]
    gross_exposure: float
    net_exposure: float


def _parse_signal(raw: dict[str, Any]) -> TradingSignal:
    positions = [
        PositionSignal(
            ticker=str(p["ticker"]),
            weight=float(p["weight"]),
            last_close=float(p.get("last_close", 0.0)),
            position_value_per_100k=float(p.get("position_value_per_100k", 0.0)),
        )
        for p in raw.get("next_day_allocation", [])
    ]
    summary = raw.get("summary", {})
    return TradingSignal(
        generated_at=str(raw.get("generated_at", "unknown")),
        model=str(raw.get("model", "unknown")),
        positions=positions,
        gross_exposure=float(summary.get("gross_exposure", sum(abs(p.weight) for p in positions))),
        net_exposure=float(summary.get("net_exposure", sum(p.weight for p in positions))),
    )


def load_latest_signal(path: Path) -> TradingSignal:
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"No signal lines in {path}")
    return _parse_signal(json.loads(lines[-1]))


def cap_signal(signal: TradingSignal, *, max_gross: float) -> TradingSignal:
    if signal.gross_exposure <= max_gross:
        return signal
    scale = max_gross / signal.gross_exposure
    positions = [
        PositionSignal(
            ticker=p.ticker,
            weight=round(p.weight * scale, 6),
            last_close=p.last_close,
            position_value_per_100k=round(p.position_value_per_100k * scale, 2),
        )
        for p in signal.positions
    ]
    return TradingSignal(
        generated_at=signal.generated_at,
        model=signal.model,
        positions=positions,
        gross_exposure=round(sum(abs(p.weight) for p in positions), 6),
        net_exposure=round(sum(p.weight for p in positions), 6),
    )
