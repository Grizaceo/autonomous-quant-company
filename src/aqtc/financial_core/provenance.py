from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .validation import load_json, summarize_walkforward

GENOTYPE_DIM = 19
MODEL_NAME = "HGAT+ES v4"
ENGINE = "Financial Lab"
ALGORITHM = "evolution_strategies"
REJECTED_NAME = "2019+ ensemble"
REJECTED_REASON = "failed recent-regime robustness"


def _production_config(data_dir: Path) -> dict[str, int]:
    toml_path = data_dir / "production.toml"
    if toml_path.exists():
        text = toml_path.read_text(encoding="utf-8")
        keys = {
            "d_model": 128,
            "pop_size": 30,
            "reward_horizon": 30,
            "rollout_horizon": 150,
            "max_generations": 50,
        }
        for key in keys:
            for line in text.splitlines():
                if line.strip().startswith(f"{key} ="):
                    try:
                        keys[key] = int(line.split("=", 1)[1].strip())
                    except ValueError:
                        pass
        return keys
    walkforward = load_json(data_dir / "walkforward_report.json")
    cfg = walkforward.get("config", {})
    return {
        "d_model": int(cfg.get("d_model", 128)),
        "pop_size": int(cfg.get("pop_size", 30)),
        "reward_horizon": int(cfg.get("reward_horizon", 30)),
        "rollout_horizon": int(cfg.get("rollout_horizon", 150)),
        "max_generations": int(cfg.get("n_generations", 50)),
    }


def load_alpha_provenance(data_dir: Path) -> dict[str, Any]:
    """Load frozen Financial Lab alpha provenance from demo artifacts."""
    walkforward = load_json(data_dir / "walkforward_report.json")
    rejected = load_json(data_dir / "rejected_ensemble_2019.json")
    accepted = summarize_walkforward(walkforward)
    rejected_metrics = summarize_walkforward(rejected)
    n_folds = int(accepted["n_folds"])
    positive_ratio = float(accepted["consistency"]) if n_folds else 0.0
    return {
        "engine": ENGINE,
        "model": MODEL_NAME,
        "algorithm": ALGORITHM,
        "genotype_dim": GENOTYPE_DIM,
        "production_config": _production_config(data_dir),
        "accepted": {
            "mean_sharpe": round(float(accepted["mean_sharpe"]), 3),
            "n_folds": n_folds,
            "positive_fold_ratio": positive_ratio,
            "mean_max_drawdown": round(float(accepted["max_drawdown"]), 3),
        },
        "rejected": {
            "name": REJECTED_NAME,
            "sharpe": round(float(rejected_metrics["mean_sharpe"]), 3),
            "max_drawdown": round(float(rejected_metrics["max_drawdown"]), 3),
            "reason": REJECTED_REASON,
        },
    }


def load_demo_manifest(data_dir: Path) -> dict[str, Any]:
    """Load frozen demo evidence bundle manifest."""
    path = data_dir / "manifest.json"
    if not path.exists():
        return load_alpha_provenance(data_dir)
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_alpha_provenance(data_dir: Path) -> str:
    p = load_alpha_provenance(data_dir)
    cfg = p["production_config"]
    accepted = p["accepted"]
    rejected = p["rejected"]
    return (
        f"{p['engine']} {p['model']} ({p['algorithm']}, {p['genotype_dim']}D genotype)\n"
        f"Accepted: Sharpe {accepted['mean_sharpe']}, "
        f"{accepted['n_folds']} folds, "
        f"{accepted['positive_fold_ratio']:.0%} positive, "
        f"MaxDD {accepted['mean_max_drawdown']}\n"
        f"Rejected: {rejected['name']} Sharpe {rejected['sharpe']}, "
        f"MaxDD {rejected['max_drawdown']} ({rejected['reason']})\n"
        f"Config: d_model={cfg['d_model']}, pop_size={cfg['pop_size']}, "
        f"reward_horizon={cfg['reward_horizon']}, "
        f"rollout_horizon={cfg['rollout_horizon']}, "
        f"max_generations={cfg['max_generations']}"
    )
