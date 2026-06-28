from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class ValidationDecision:
    accepted: bool
    reason: str
    mean_sharpe: float
    max_drawdown: float
    consistency: float
    n_folds: int


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_walkforward(report: dict[str, Any]) -> dict[str, float | int]:
    summary = report.get("summary") or report.get("metrics") or {}
    return {
        "mean_sharpe": float(summary.get("mean_sharpe", summary.get("sharpe", 0.0))),
        "max_drawdown": float(summary.get("mean_max_drawdown", summary.get("max_drawdown", 1.0))),
        "consistency": float(summary.get("sharpe_consistent", 0.0)),
        "n_folds": int(summary.get("n_folds", len(report.get("folds", [])) or 1)),
    }


def passes_gate4(
    report: dict[str, Any],
    *,
    min_sharpe: float = 1.0,
    max_drawdown: float = 0.15,
    min_consistency: float = 0.8,
) -> ValidationDecision:
    s = summarize_walkforward(report)
    accepted = (
        s["mean_sharpe"] >= min_sharpe
        and s["max_drawdown"] <= max_drawdown
        and s["consistency"] >= min_consistency
    )
    if accepted:
        reason = (
            f"accepted: Sharpe {s['mean_sharpe']:.3f}, "
            f"MaxDD {s['max_drawdown']:.3f}, consistency {s['consistency']:.0%}"
        )
    else:
        reason = (
            f"rejected: Sharpe {s['mean_sharpe']:.3f}, "
            f"MaxDD {s['max_drawdown']:.3f}, consistency {s['consistency']:.0%}"
        )
    return ValidationDecision(
        accepted=accepted,
        reason=reason,
        mean_sharpe=s["mean_sharpe"],
        max_drawdown=s["max_drawdown"],
        consistency=s["consistency"],
        n_folds=s["n_folds"],
    )


def compare_candidate_vs_rejected(candidate: dict[str, Any], rejected: dict[str, Any]) -> dict[str, float]:
    c = summarize_walkforward(candidate)
    r = summarize_walkforward(rejected)
    return {
        "candidate_sharpe": c["mean_sharpe"],
        "rejected_sharpe": r["mean_sharpe"],
        "sharpe_delta": c["mean_sharpe"] - r["mean_sharpe"],
        "candidate_max_drawdown": c["max_drawdown"],
        "rejected_max_drawdown": r["max_drawdown"],
        "drawdown_delta": r["max_drawdown"] - c["max_drawdown"],
    }
