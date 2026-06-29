#!/usr/bin/env python3
"""Regenerate hash-addressed proof manifest for submission artifacts."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "data" / "demo" / "proof_manifest.generated.json"

PROOF_PATHS = [
    REPO_ROOT / "data" / "demo" / "walkforward_report.json",
    REPO_ROOT / "data" / "demo" / "rejected_ensemble_2019.json",
    REPO_ROOT / "data" / "demo" / "production.toml",
    REPO_ROOT / "data" / "demo" / "live_signals.jsonl",
    REPO_ROOT / "data" / "demo" / "manifest.json",
    REPO_ROOT / "docs" / "proof" / "stripe_test_paymentintent_redacted.json",
    REPO_ROOT / "samples" / "customer_report.md",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def main() -> None:
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    artifacts: list[dict[str, object]] = []
    for path in PROOF_PATHS:
        if not path.exists():
            continue
        artifacts.append(
            {
                "path": rel(path),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "generated_at": generated_at,
            }
        )
    manifest = {
        "bundle": "aqtc-proof-manifest",
        "version": "1.0.0",
        "generated_at": generated_at,
        "artifacts": artifacts,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {rel(OUTPUT)} ({len(artifacts)} artifacts)")


if __name__ == "__main__":
    main()
