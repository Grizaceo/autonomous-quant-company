from __future__ import annotations

import json
import shutil
from pathlib import Path

from aqtc.config import AQTCConfig
from aqtc.financial_core.strategy_integrity import verify_strategy_artifacts
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR, REPO_ROOT


def _copy_demo_tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    demo_dir = root / "data" / "demo"
    demo_dir.parent.mkdir(parents=True)
    shutil.copytree(DEMO_DATA_DIR, demo_dir)
    return root


def test_verify_strategy_artifacts_accepts_current_manifest():
    result = verify_strategy_artifacts(repo_root=REPO_ROOT)

    assert result.ok is True
    assert result.checked_count >= 5
    assert result.failures == []
    assert "data/demo/walkforward_report.json" in result.checked_paths
    assert "data/demo/production.toml" in result.checked_paths


def test_verify_strategy_artifacts_detects_tampered_file(tmp_path):
    root = _copy_demo_tree(tmp_path)
    target = root / "data" / "demo" / "walkforward_report.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["tamper_marker"] = "judge changed the evidence"
    target.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    result = verify_strategy_artifacts(repo_root=root)

    assert result.ok is False
    assert result.checked_count >= 5
    assert any(f.path == "data/demo/walkforward_report.json" for f in result.failures)
    assert any(f.reason == "sha256_mismatch" for f in result.failures)


def test_daily_cycle_blocks_paper_rebalance_when_strategy_artifact_tampered(tmp_path):
    root = _copy_demo_tree(tmp_path)
    demo_dir = root / "data" / "demo"
    target = demo_dir / "walkforward_report.json"
    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["tamper_marker"] = "mutated after proof manifest generation"
    target.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    cfg = AQTCConfig(demo_data_dir=demo_dir, state_dir=tmp_path / "state")
    agent = AutonomousQuantCompanyAgent(cfg)
    result = agent.run_daily_cycle()
    events = agent.events.read()

    assert result.strategy_integrity_ok is False
    assert result.strategy_integrity_status == "blocked"
    assert result.portfolio_positions == 0
    assert "verify_strategy_integrity" in [event["action"] for event in events]
    integrity_event = [event for event in events if event["action"] == "verify_strategy_integrity"][
        -1
    ]
    assert integrity_event["approval_status"] == "blocked"
    assert integrity_event["evidence"]["failures"][0]["reason"] == "sha256_mismatch"
