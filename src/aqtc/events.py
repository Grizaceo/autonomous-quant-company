from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class BusinessEvent:
    actor: str
    action: str
    summary: str
    amount_usd: float = 0.0
    approval_status: str = "not_required"
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _canonical_event_json(event: dict[str, Any]) -> str:
    payload = dict(event)
    payload.pop("hash", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _event_hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_event_json(event).encode("utf-8")).hexdigest()


class EventLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def _last_hash(self) -> str | None:
        for event in reversed(self.read()):
            value = event.get("hash")
            if isinstance(value, str) and value:
                return value
        return None

    def append(self, event: BusinessEvent) -> None:
        entry = event.to_dict()
        entry["prev_hash"] = self._last_hash()
        entry["hash"] = _event_hash(entry)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out

    def verify_chain(self) -> dict[str, Any]:
        """Verify hash-chained events while accepting pre-hash legacy prefixes.

        Legacy entries without hash fields are accepted only before the first hashed
        event. Once the chain starts, a missing hash is treated as tampering because
        removing hash fields would otherwise be a trivial bypass.
        """
        events = self.read()
        previous_hash: str | None = None
        chain_started = False
        for index, event in enumerate(events):
            has_hash = isinstance(event.get("hash"), str) and isinstance(
                event.get("prev_hash"), str | type(None)
            )
            if not has_hash:
                if chain_started:
                    return {
                        "ok": False,
                        "count": len(events),
                        "first_bad_index": index,
                        "reason": "missing_hash_after_chain_started",
                    }
                continue
            chain_started = True
            if event.get("prev_hash") != previous_hash:
                return {
                    "ok": False,
                    "count": len(events),
                    "first_bad_index": index,
                    "reason": "prev_hash_mismatch",
                }
            if event["hash"] != _event_hash(event):
                return {
                    "ok": False,
                    "count": len(events),
                    "first_bad_index": index,
                    "reason": "hash_mismatch",
                }
            previous_hash = event["hash"]
        return {"ok": True, "count": len(events), "first_bad_index": None, "reason": None}
