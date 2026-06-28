from aqtc.integrations.nemoclaw import LocalPolicyApprovalAdapter, load_approval_policy
from aqtc.paths import REPO_ROOT


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
