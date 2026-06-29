from aqtc.config import AQTCConfig
from aqtc.integrations.nemoclaw import LocalPolicyApprovalAdapter, load_approval_policy
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR, REPO_ROOT


def test_load_policy_yaml():
    policy = load_approval_policy(REPO_ROOT / "examples" / "approval_policy.yaml")
    assert policy.policy_id == "aqtc-hackathon-demo-v1"
    assert policy.max_gross_exposure == 4.0
    assert policy.live_trading is False


def test_spend_requires_approval_above_threshold():
    policy = load_approval_policy(REPO_ROOT / "examples" / "approval_policy.yaml")
    decision = LocalPolicyApprovalAdapter(policy).review_spend(amount_usd=6.0)
    assert decision.approved is False
    assert decision.status == "requires_human_approval"


def test_spend_allowed_under_threshold():
    policy = load_approval_policy(REPO_ROOT / "examples" / "approval_policy.yaml")
    decision = LocalPolicyApprovalAdapter(policy).review_spend(amount_usd=2.0)
    assert decision.approved is True
    assert decision.status == "approved"


def test_deny_live_broker_execution():
    policy = load_approval_policy(REPO_ROOT / "examples" / "approval_policy.yaml")
    from aqtc.financial_core.risk import RiskAssessment

    assessment = RiskAssessment(
        allowed=True,
        reasons=[],
        gross_exposure=1.0,
        active_positions=1,
    )
    decision = LocalPolicyApprovalAdapter(policy).review_trade(assessment, live_requested=True)
    assert decision.approved is False
    assert decision.status == "blocked"
    assert "live_broker_execution" in decision.reason


def test_spend_skipped_when_requires_human_approval(tmp_path):
    cfg = AQTCConfig(
        demo_data_dir=DEMO_DATA_DIR,
        state_dir=tmp_path,
        data_purchase_usd=6.0,
        auto_approve_spend=False,
    )
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    assert result.spend_status == "skipped_pending_approval"
    assert result.stripe_net_usd == 19.0


def test_spend_auto_approved_with_flag(tmp_path):
    cfg = AQTCConfig(
        demo_data_dir=DEMO_DATA_DIR,
        state_dir=tmp_path,
        data_purchase_usd=6.0,
        auto_approve_spend=True,
    )
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    assert result.spend_status == "completed"
    assert result.stripe_net_usd == 13.0


def test_trade_blocked_skips_execution(tmp_path, monkeypatch):
    from aqtc.financial_core.risk import RiskAssessment

    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path, live_trading=True)

    def fake_assess(self, signal, live_requested=False):
        return RiskAssessment(
            allowed=False,
            reasons=["forced block for test"],
            gross_exposure=99.0,
            active_positions=1,
        )

    monkeypatch.setattr("aqtc.operations.business_cycle.RiskGuard.assess", fake_assess)
    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()
    assert result.approval_status == "blocked"
    assert result.portfolio_positions == 0


def test_live_request_is_blocked_by_default_policy(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path, live_trading=True)

    result = AutonomousQuantCompanyAgent(cfg).run_daily_cycle()

    assert result.approval_status == "blocked"
    assert result.portfolio_positions == 0
    events = AutonomousQuantCompanyAgent(cfg).events.read()
    approve_trade = [event for event in events if event["action"] == "approve_trade"][-1]
    assert approve_trade["approval_status"] == "blocked"
    assert "live_broker_execution" in approve_trade["summary"]
