import pytest

from aqtc import mcp_server
from aqtc.config import AQTCConfig
from aqtc.operations.business_cycle import AutonomousQuantCompanyAgent
from aqtc.paths import DEMO_DATA_DIR


@pytest.fixture
def isolated_mcp(tmp_path, monkeypatch):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("AQTC_DISABLE_HERMES_ENV", "true")
    mcp_server.reset_agent()
    cfg = AQTCConfig(demo_data_dir=DEMO_DATA_DIR, state_dir=tmp_path)
    agent = AutonomousQuantCompanyAgent(cfg)
    mcp_server._agent_instance = agent
    yield agent
    mcp_server.reset_agent()


def test_mcp_tool_functions_return_dicts(isolated_mcp):
    result = mcp_server.aqtc_run_cycle(reset=True)
    assert result["accepted_strategy"] is True
    assert result["rejected_bad_strategy"] is True
    status = mcp_server.aqtc_status()
    assert "events" in status
    report = mcp_server.aqtc_get_report()
    assert "Autonomous Quant Company Report" in report["content"]
    events = mcp_server.aqtc_get_events()
    assert events["count"] >= 1


def test_mcp_get_report_read_only(isolated_mcp, tmp_path):
    report_path = tmp_path / "customer_report.md"
    report_path.write_text("# Existing report\n", encoding="utf-8")
    content = mcp_server.aqtc_get_report(run=False)["content"]
    assert content.startswith("# Existing report")


def test_mcp_module_exports_tools():
    if mcp_server.FastMCP is None:
        pytest.skip("fastmcp not installed")
    assert mcp_server.mcp is not None
