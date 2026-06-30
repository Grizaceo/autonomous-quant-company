import json

from aqtc.events import BusinessEvent, EventLog


def test_event_hash_chain_verifies_clean_log(tmp_path):
    log = EventLog(tmp_path / "events.jsonl")
    log.append(BusinessEvent(actor="a", action="one", summary="first"))
    log.append(BusinessEvent(actor="a", action="two", summary="second"))

    events = log.read()
    assert events[0]["prev_hash"] is None
    assert events[0]["hash"]
    assert events[1]["prev_hash"] == events[0]["hash"]
    assert log.verify_chain() == {"ok": True, "count": 2, "first_bad_index": None, "reason": None}


def test_event_hash_chain_detects_tampering(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(BusinessEvent(actor="a", action="one", summary="first"))
    log.append(BusinessEvent(actor="a", action="two", summary="second"))

    events = log.read()
    events[0]["summary"] = "tampered"
    path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n")

    result = log.verify_chain()
    assert result["ok"] is False
    assert result["first_bad_index"] == 0
    assert result["reason"] == "hash_mismatch"


def test_event_hash_chain_accepts_legacy_entries_as_unverified_legacy(tmp_path):
    path = tmp_path / "events.jsonl"
    legacy = {"actor": "legacy", "action": "old", "summary": "pre hash"}
    path.write_text(json.dumps(legacy) + "\n", encoding="utf-8")

    log = EventLog(path)
    assert log.verify_chain() == {"ok": True, "count": 1, "first_bad_index": None, "reason": None}
    log.append(BusinessEvent(actor="new", action="hash", summary="starts chain"))
    events = log.read()
    assert "hash" not in events[0]
    assert events[1]["prev_hash"] is None
    assert log.verify_chain()["ok"] is True


def test_event_hash_chain_rejects_legacy_entry_after_chain_started(tmp_path):
    path = tmp_path / "events.jsonl"
    log = EventLog(path)
    log.append(BusinessEvent(actor="a", action="one", summary="first"))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"actor": "legacy", "action": "late", "summary": "bad"}) + "\n")

    result = log.verify_chain()
    assert result["ok"] is False
    assert result["first_bad_index"] == 1
    assert result["reason"] == "missing_hash_after_chain_started"
