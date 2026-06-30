import json

import pytest

from aqtc.config import AQTCConfig
from aqtc.events import BusinessEvent, EventLog
from aqtc.financial_core.portfolio import MockBroker, PortfolioState
from aqtc.financial_core.signals import (
    PositionSignal,
    TradingSignal,
    cap_signal,
    load_latest_signal,
)


def _signal(weights):
    positions = [
        PositionSignal(
            ticker=f"T{i}", weight=w, last_close=10 + i, position_value_per_100k=w * 100000
        )
        for i, w in enumerate(weights)
    ]
    return TradingSignal(
        generated_at="2026-01-01T00:00:00Z",
        model="test",
        positions=positions,
        gross_exposure=sum(abs(w) for w in weights),
        net_exposure=sum(weights),
    )


def test_config_defaults_are_safe(monkeypatch):
    monkeypatch.delenv("AQTC_LIVE_TRADING", raising=False)
    cfg = AQTCConfig()
    assert cfg.live_trading is False
    assert cfg.stripe_mode == "mock"
    assert cfg.nvidia_mode == "mock"


def test_config_env_overrides_are_applied_at_instantiation(monkeypatch, tmp_path):
    monkeypatch.setenv("AQTC_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AQTC_STRIPE_MODE", "stripe_test")
    monkeypatch.setenv("AQTC_NVIDIA_MODE", "auto")
    monkeypatch.setenv("AQTC_REPORT_PRICE_USD", "25.5")
    cfg = AQTCConfig()
    assert cfg.state_dir == tmp_path / "state"
    assert cfg.stripe_mode == "stripe_test"
    assert cfg.nvidia_mode == "auto"
    assert cfg.report_price_usd == 25.5


def test_config_ensure_state_creates_state_dir(tmp_path):
    cfg = AQTCConfig(state_dir=tmp_path / "new-state")
    cfg.ensure_state()
    assert cfg.state_dir.is_dir()


def test_cap_signal_preserves_relative_weights():
    capped = cap_signal(_signal([3.0, -1.0]), max_gross=2.0)
    assert capped.gross_exposure == pytest.approx(2.0)
    assert capped.positions[0].weight == pytest.approx(1.5)
    assert capped.positions[1].weight == pytest.approx(-0.5)


def test_cap_signal_noop_under_limit():
    signal = _signal([0.5, -0.25])
    assert cap_signal(signal, max_gross=4.0) is signal


def test_load_latest_signal_reads_last_jsonl_entry(tmp_path):
    path = tmp_path / "signals.jsonl"
    first = {"generated_at": "old", "model": "m1", "next_day_allocation": [], "summary": {}}
    second = {
        "generated_at": "new",
        "model": "m2",
        "next_day_allocation": [{"ticker": "AAPL", "weight": 1.0, "last_close": 10}],
        "summary": {"gross_exposure": 1.0, "net_exposure": 1.0},
    }
    path.write_text(json.dumps(first) + "\n" + json.dumps(second) + "\n", encoding="utf-8")
    signal = load_latest_signal(path)
    assert signal.generated_at == "new"
    assert signal.positions[0].ticker == "AAPL"


def test_mock_broker_initial_state(tmp_path):
    broker = MockBroker(tmp_path / "portfolio.json")
    state = broker.load()
    assert state == PortfolioState()
    assert state.mode == "paper"


def test_mock_broker_rebalance_persists_positions(tmp_path):
    broker = MockBroker(tmp_path / "portfolio.json")
    state = broker.rebalance(_signal([0.25, -0.1]))
    assert state.positions == {"T0": 0.25, "T1": -0.1}
    assert MockBroker(tmp_path / "portfolio.json").load().positions == state.positions


def test_event_log_empty_read(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    assert log.read() == []


def test_event_log_append_then_read(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append(BusinessEvent(actor="tester", action="check", summary="ok"))
    [event] = log.read()
    assert event["actor"] == "tester"
    assert event["action"] == "check"
    assert event["timestamp"]


def test_event_log_persists_across_instances(tmp_path):
    path = tmp_path / "events.jsonl"
    EventLog(path).append(BusinessEvent(actor="tester", action="persist", summary="ok"))
    assert EventLog(path).read()[0]["action"] == "persist"
