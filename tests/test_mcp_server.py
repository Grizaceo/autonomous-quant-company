from aqtc import mcp_server


def test_mcp_tool_functions_return_dicts(tmp_path, monkeypatch):
    # Direct function smoke test keeps CI independent of a running MCP client.
    result = mcp_server.aqtc_run_cycle(reset=True)
    assert result["accepted_strategy"] is True
    assert result["rejected_bad_strategy"] is True
    status = mcp_server.aqtc_status()
    assert "events" in status
    report = mcp_server.aqtc_get_report()
    assert "Autonomous Quant Company Report" in report["content"]
    events = mcp_server.aqtc_get_events()
    assert events["count"] >= 1
