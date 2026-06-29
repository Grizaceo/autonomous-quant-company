from pathlib import Path

from aqtc.financial_core.validation import compare_candidate_vs_rejected, load_json, passes_gate4

DATA = Path(__file__).resolve().parents[1] / "data" / "demo"


def test_production_walkforward_passes_gate4():
    report = load_json(DATA / "walkforward_report.json")
    decision = passes_gate4(report)
    assert decision.accepted is True
    assert decision.mean_sharpe > 3.0
    assert decision.n_folds == 5


def test_rejected_ensemble_fails_gate4():
    report = load_json(DATA / "rejected_ensemble_2019.json")
    decision = passes_gate4(report)
    assert decision.accepted is False
    assert decision.mean_sharpe < 0
    assert decision.max_drawdown > 0.4


def test_candidate_beats_rejected():
    candidate = load_json(DATA / "walkforward_report.json")
    rejected = load_json(DATA / "rejected_ensemble_2019.json")
    comparison = compare_candidate_vs_rejected(candidate, rejected)
    assert comparison["sharpe_delta"] > 3.7
    assert comparison["drawdown_delta"] > 0.4
