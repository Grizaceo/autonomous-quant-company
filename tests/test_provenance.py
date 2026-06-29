import pytest

from aqtc.financial_core.provenance import (
    load_alpha_provenance,
    load_demo_manifest,
    summarize_alpha_provenance,
)
from aqtc.paths import DEMO_DATA_DIR


def test_load_alpha_provenance_structure():
    p = load_alpha_provenance(DEMO_DATA_DIR)
    assert p["engine"] == "Financial Lab"
    assert p["model"] == "HGAT+ES v4"
    assert p["algorithm"] == "evolution_strategies"
    assert p["genotype_dim"] == 19
    assert p["accepted"]["mean_sharpe"] == pytest.approx(3.255, abs=0.01)
    assert p["accepted"]["n_folds"] == 5
    assert p["accepted"]["positive_fold_ratio"] == 1.0
    assert p["accepted"]["mean_max_drawdown"] == pytest.approx(0.032, abs=0.01)
    assert p["rejected"]["name"] == "2019+ ensemble"
    assert p["rejected"]["sharpe"] == pytest.approx(-0.544, abs=0.01)
    assert p["rejected"]["max_drawdown"] == pytest.approx(0.486, abs=0.01)
    assert p["rejected"]["reason"] == "failed recent-regime robustness"
    assert p["production_config"]["d_model"] == 128
    assert p["production_config"]["pop_size"] == 30


def test_summarize_alpha_provenance_contains_key_metrics():
    text = summarize_alpha_provenance(DEMO_DATA_DIR)
    assert "HGAT+ES v4" in text
    assert "3.255" in text
    assert "-0.544" in text


def test_load_demo_manifest():
    m = load_demo_manifest(DEMO_DATA_DIR)
    assert m["bundle"] == "aqtc-demo-evidence"
    assert m["model"] == "HGAT+ES v4"
    assert m["accepted"]["mean_sharpe"] == 3.255
    assert "walkforward_report" in m["artifacts"]
