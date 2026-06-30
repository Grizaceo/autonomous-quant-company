import json

from aqtc.config import AQTCConfig
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR


def _run(tmp_path, **overrides):
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path, **overrides)
    agent = AutonomousQuantCompanyAgent(cfg)
    return agent, agent.run_daily_cycle()


def test_daily_cycle_is_deterministic_in_mock_mode(tmp_path):
    agent, first = _run(tmp_path)
    second = agent.run_daily_cycle(reset=True)
    assert first.to_dict() | {"report_path": "<path>"} == second.to_dict() | {
        "report_path": "<path>"
    }


def test_daily_cycle_logs_expected_actions_in_order(tmp_path):
    agent, _ = _run(tmp_path)
    actions = [event["action"] for event in agent.events.read()]
    assert actions == [
        "summarize_regime",
        "approve_spend",
        "spend",
        "validate_strategy",
        "reject_strategy",
        "approve_trade",
        "execute_paper_rebalance",
        "earn",
        "generate_report",
    ]


def test_daily_cycle_spend_requires_approval_above_threshold(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_DATA_PURCHASE_USD", "6")
    agent, result = _run(tmp_path)
    assert result.spend_status == "skipped_pending_approval"
    assert result.spend_approval_status == "requires_human_approval"
    assert agent.ledger.net() == 19.0


def test_daily_cycle_auto_approve_spend_changes_net_result(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_DATA_PURCHASE_USD", "6")
    _, result = _run(tmp_path, auto_approve_spend=True)
    assert result.spend_status == "completed"
    assert result.stripe_net_usd == 13.0


def test_daily_cycle_never_executes_live_broker_by_default(tmp_path):
    agent, result = _run(tmp_path)
    assert result.approval_status == "approved"
    assert agent.broker.load().mode == "paper"
    assert result.nemotron_live is False


def test_daily_cycle_portfolio_gross_exposure_within_policy(tmp_path):
    agent, result = _run(tmp_path)
    assert result.gross_exposure <= agent.policy.max_gross_exposure
    assert result.portfolio_positions <= agent.policy.max_active_positions


def test_daily_cycle_rejects_bad_strategy_even_when_good_strategy_accepted(tmp_path):
    _, result = _run(tmp_path)
    assert result.accepted_strategy is True
    assert result.rejected_bad_strategy is True
    assert result.accepted_candidate_sharpe is not None
    assert result.rejected_candidate_sharpe is not None
    assert result.accepted_candidate_sharpe > 3
    assert result.rejected_candidate_sharpe < 0


def test_daily_cycle_result_is_json_serializable(tmp_path):
    _, result = _run(tmp_path)
    encoded = json.dumps(result.to_dict(), sort_keys=True)
    assert "accepted_strategy" in encoded
