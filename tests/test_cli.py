import json

from aqtc.cli import main


def test_cli_demo_json(isolated_env, capsys):
    code = main(["demo", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["stripe_net_usd"] == 17.0
    assert data["accepted_strategy"] is True


def test_cli_status(isolated_env, capsys):
    main(["demo", "--json"])
    capsys.readouterr()
    code = main(["status"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert "events" in data
    assert "ledger" in data


def test_cli_report_read_only(isolated_env, tmp_path):
    report_src = isolated_env / "customer_report.md"
    report_src.write_text("# saved report\n", encoding="utf-8")
    out = tmp_path / "copy.md"
    code = main(["report", "--out", str(out)])
    assert code == 0
    assert out.read_text(encoding="utf-8") == "# saved report\n"


def test_cli_report_run(isolated_env, tmp_path):
    out = tmp_path / "fresh.md"
    code = main(["report", "--run", "--out", str(out)])
    assert code == 0
    assert "Autonomous Quant Company Report" in out.read_text(encoding="utf-8")


def test_cli_regime_json(isolated_env, capsys):
    code = main(["regime", "--provider", "mock", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["provider"] == "mock-nemotron"


def test_cli_report_missing_without_run(isolated_env, tmp_path):
    out = tmp_path / "missing.md"
    try:
        main(["report", "--out", str(out)])
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError when no report exists")


def test_cli_demo_approve_spend_flag(isolated_env, capsys, monkeypatch):
    monkeypatch.setenv("AQTC_DATA_PURCHASE_USD", "6")
    code = main(["demo", "--approve-spend", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["spend_status"] == "completed"
