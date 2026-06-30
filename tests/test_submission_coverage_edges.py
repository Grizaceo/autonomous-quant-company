import io
import json
import urllib.error
from email.message import Message
from unittest.mock import patch

import pytest

from aqtc import mcp_server
from aqtc.cli import main
from aqtc.config import AQTCConfig
from aqtc.financial_core.provenance import load_demo_manifest
from aqtc.integrations.stripe_skills import StripeLedger, StripeTestModeAdapter
from aqtc.paths import DEMO_DATA_DIR


def test_cli_demo_human_output_contract(isolated_env, capsys):
    code = main(["demo"])
    out = capsys.readouterr().out
    assert code == 0
    assert "AQTC Daily Cycle Complete" in out
    assert "DECISIONS (agent-visible)" in out
    assert "validate_strategy: accept=True" in out
    assert "reject_strategy: rejected=True" in out
    assert "stripe_earn:" in out
    assert "events_logged:" in out


def test_cli_regime_human_output_contract(isolated_env, capsys):
    code = main(["regime", "--provider", "mock"])
    out = capsys.readouterr().out
    assert code == 0
    assert "provider: mock-nemotron" in out
    assert "live: False" in out
    assert "paper mode" in out


def test_cli_demo_modes_and_policy_flags(isolated_env, tmp_path, capsys):
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        "policy_id: custom-test\n"
        "budget:\n"
        "  daily_budget_usd: 25\n"
        "  require_approval_above_usd: 5\n"
        "risk:\n"
        "  max_gross_exposure: 4\n"
        "  max_active_positions: 8\n"
        "  max_single_position_weight: 2\n"
        "actions:\n"
        "  deny: [live_broker_execution]\n"
        "  require_approval: [spend_above_threshold]\n",
        encoding="utf-8",
    )
    code = main([
        "demo",
        "--json",
        "--stripe-mode",
        "stripe_test",
        "--nvidia-mode",
        "mock",
        "--policy",
        str(policy),
    ])
    data = json.loads(capsys.readouterr().out)
    assert code == 0
    assert data["stripe_mode"] == "stripe_test"
    assert data["nemotron_provider"] == "mock-nemotron"


def test_cli_exception_path_reports_runtime_error(monkeypatch, capsys):
    monkeypatch.setenv("AQTC_REPORT_PRICE_USD", "not-a-float")
    code = main(["demo", "--json"])
    err = capsys.readouterr().err
    assert code == 1
    assert "aqtc: ValueError" in err


@patch("aqtc.integrations.stripe_skills.get_secret", return_value=None)
def test_stripe_test_mode_spend_upgrades_mock_event(mock_secret, tmp_path):
    ledger = StripeLedger(tmp_path / "ledger.json")
    adapter = StripeTestModeAdapter(ledger)
    event = adapter.spend("data", 2.0)
    assert event.mode == "stripe_test"
    assert event.status == "budgeted_procurement_recorded"
    assert event.metadata["note"].startswith("Outbound Stripe")
    assert ledger.read()[-1]["status"] == "budgeted_procurement_recorded"


@patch("aqtc.integrations.stripe_skills.get_secret", return_value=None)
def test_stripe_post_form_without_key_raises(mock_secret, tmp_path):
    adapter = StripeTestModeAdapter(StripeLedger(tmp_path / "ledger.json"))
    with pytest.raises(RuntimeError, match="STRIPE_SECRET_KEY"):
        adapter._post_form("/payment_intents", {"amount": 100})


@patch("aqtc.integrations.stripe_skills.get_secret", return_value="sk_test_placeholder")
def test_stripe_post_form_http_error_includes_body(mock_secret, tmp_path):
    adapter = StripeTestModeAdapter(StripeLedger(tmp_path / "ledger.json"))
    error = urllib.error.HTTPError(
        url="https://api.stripe.com/v1/payment_intents",
        code=402,
        msg="Payment Required",
        hdrs=Message(),
        fp=io.BytesIO(b'{"error":"card_declined"}'),
    )
    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(RuntimeError, match="Stripe API error 402"):
            adapter._post_form("/payment_intents", {"amount": 100})


def test_mcp_agent_with_explicit_config_does_not_mutate_singleton(tmp_path):
    mcp_server.reset_agent()
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    explicit = mcp_server._agent(cfg)
    assert explicit.config.state_dir == tmp_path
    assert mcp_server._agent_instance is None
    implicit = mcp_server._agent()
    assert mcp_server._agent_instance is implicit
    mcp_server.reset_agent()


def test_mcp_main_requires_fastmcp_when_unavailable(monkeypatch):
    monkeypatch.setattr(mcp_server, "mcp", None)
    with pytest.raises(RuntimeError, match="fastmcp is required"):
        mcp_server.main()


def test_load_demo_manifest_falls_back_to_provenance_when_manifest_missing(tmp_path):
    for name in ["walkforward_report.json", "rejected_ensemble_2019.json", "production.toml"]:
        (tmp_path / name).write_bytes((DEMO_DATA_DIR / name).read_bytes())
    manifest = load_demo_manifest(tmp_path)
    assert manifest["model"] == "HGAT+ES v4"
    assert manifest["accepted"]["mean_sharpe"] == pytest.approx(3.255, abs=0.01)
