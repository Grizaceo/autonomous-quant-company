from aqtc.config import AQTCConfig
from aqtc.integrations.nemoclaw import load_approval_policy


def test_config_reads_env_at_instantiation(monkeypatch, tmp_path):
    monkeypatch.setenv("AQTC_STRIPE_MODE", "stripe_test")
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    cfg = AQTCConfig()
    assert cfg.stripe_mode == "stripe_test"
    assert cfg.state_dir == tmp_path


def test_policy_env_override_only_when_set(monkeypatch, tmp_path):
    from aqtc.paths import REPO_ROOT

    policy_path = REPO_ROOT / "examples" / "approval_policy.yaml"
    policy = load_approval_policy(policy_path)
    assert policy.daily_budget_usd == 25.0

    monkeypatch.setenv("AQTC_DAILY_BUDGET_USD", "10")
    policy = load_approval_policy(policy_path)
    assert policy.daily_budget_usd == 10.0
    assert policy.require_approval_above_usd == 5.0
