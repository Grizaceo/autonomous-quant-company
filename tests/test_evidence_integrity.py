import hashlib
import json
import tomllib
from pathlib import Path

import pytest

from aqtc.config import AQTCConfig
from aqtc.financial_core.provenance import load_alpha_provenance
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR, REPO_ROOT

PROOF_MANIFEST = DEMO_DATA_DIR / "proof_manifest.generated.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_proof_manifest_loads():
    manifest = _load_json(PROOF_MANIFEST)
    assert manifest["bundle"] == "aqtc-proof-manifest"
    assert manifest["version"] == "1.0.0"
    assert isinstance(manifest["artifacts"], list)
    assert len(manifest["artifacts"]) >= 7


def test_proof_manifest_has_required_artifacts():
    manifest = _load_json(PROOF_MANIFEST)
    paths = {artifact["path"] for artifact in manifest["artifacts"]}
    assert {
        "data/demo/walkforward_report.json",
        "data/demo/rejected_ensemble_2019.json",
        "data/demo/production.toml",
        "data/demo/live_signals.jsonl",
        "data/demo/manifest.json",
        "docs/proof/stripe_test_paymentintent_redacted.json",
        "samples/customer_report.md",
    }.issubset(paths)


@pytest.mark.parametrize("artifact", _load_json(PROOF_MANIFEST)["artifacts"])
def test_proof_manifest_hashes_match_current_files(artifact):
    path = REPO_ROOT / artifact["path"]
    assert path.exists(), artifact["path"]
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == artifact["sha256"]
    assert len(data) == artifact["size_bytes"]


def test_walkforward_report_summary_matches_claims():
    report = _load_json(DEMO_DATA_DIR / "walkforward_report.json")
    summary = report["summary"]
    assert summary["mean_sharpe"] == pytest.approx(3.2550466115)
    assert summary["n_folds"] == 5
    assert summary["sharpe_consistent"] == 1.0
    assert all(fold["sharpe"] > 0 for fold in report["folds"])


def test_rejected_ensemble_summary_matches_claims():
    rejected = _load_json(DEMO_DATA_DIR / "rejected_ensemble_2019.json")
    metrics = rejected["metrics"]
    assert metrics["sharpe"] == pytest.approx(-0.5435216997)
    assert metrics["max_drawdown"] == pytest.approx(0.4863542286)
    assert metrics["total_return"] < 0


def test_production_toml_matches_provenance_config():
    production = tomllib.loads((DEMO_DATA_DIR / "production.toml").read_text(encoding="utf-8"))
    provenance = load_alpha_provenance(DEMO_DATA_DIR)
    cfg = provenance["production_config"]
    assert production["es"]["d_model"] == cfg["d_model"] == 128
    assert production["es"]["pop_size"] == cfg["pop_size"] == 30
    assert production["data"]["reward_horizon"] == cfg["reward_horizon"] == 30
    assert production["es"]["rollout_horizon"] == cfg["rollout_horizon"] == 150
    assert production["es"]["max_generations"] == cfg["max_generations"] == 50


def test_customer_report_contains_falsification_section_after_cycle(tmp_path):
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    report = Path(result.report_path).read_text(encoding="utf-8")
    assert "## What was rejected" in report
    assert "2019+ ensemble" in report
    assert "Sharpe: -0.544" in report
    assert "failed recent-regime robustness" in report


def test_customer_report_contains_not_investment_advice_after_cycle(tmp_path):
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    report = Path(result.report_path).read_text(encoding="utf-8")
    assert "## Not investment advice" in report
    assert "No investment advice" in report
    assert "no live broker execution" in report
