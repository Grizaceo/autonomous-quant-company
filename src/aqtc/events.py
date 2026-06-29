from __future__ import annotations

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


class EventLog:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("")

    def append(self, event: BusinessEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
        return out
