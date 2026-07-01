from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REQUIRED_STRATEGY_ARTIFACTS = frozenset(
    {
        "data/demo/walkforward_report.json",
        "data/demo/rejected_ensemble_2019.json",
        "data/demo/production.toml",
        "data/demo/live_signals.jsonl",
        "data/demo/manifest.json",
    }
)


@dataclass(frozen=True)
class StrategyIntegrityFailure:
    path: str
    reason: str
    expected_sha256: str | None = None
    actual_sha256: str | None = None
    expected_size_bytes: int | None = None
    actual_size_bytes: int | None = None


@dataclass(frozen=True)
class StrategyIntegrityResult:
    ok: bool
    manifest_path: str
    checked_paths: list[str]
    failures: list[StrategyIntegrityFailure]

    @property
    def checked_count(self) -> int:
        return len(self.checked_paths)

    @property
    def status(self) -> str:
        return "verified" if self.ok else "blocked"

    @property
    def summary(self) -> str:
        if self.ok:
            return f"strategy artifacts verified from disk ({self.checked_count} SHA-256 checks)"
        return (
            "strategy artifact integrity failed; refusing paper rebalance "
            f"({len(self.failures)} failure(s))"
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["checked_count"] = self.checked_count
        payload["status"] = self.status
        return payload


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_repo_root_from_demo_dir(demo_data_dir: Path) -> Path:
    """Infer the repo root from a `data/demo` directory.

    Tests copy demo artifacts under a temporary repo root. Production uses the
    real repository root. Both shapes keep the manifest's relative paths valid.
    """
    resolved = demo_data_dir.resolve()
    if resolved.name == "demo" and resolved.parent.name == "data":
        return resolved.parent.parent
    return resolved.parent


def _load_manifest(
    manifest_path: Path,
) -> tuple[dict[str, Any] | None, StrategyIntegrityFailure | None]:
    if not manifest_path.exists():
        return None, StrategyIntegrityFailure(
            path=manifest_path.as_posix(),
            reason="manifest_missing",
        )
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, StrategyIntegrityFailure(
            path=manifest_path.as_posix(),
            reason="manifest_invalid_json",
        )
    if not isinstance(raw, dict) or not isinstance(raw.get("artifacts"), list):
        return None, StrategyIntegrityFailure(
            path=manifest_path.as_posix(),
            reason="manifest_invalid_schema",
        )
    return raw, None


def verify_strategy_artifacts(
    *,
    repo_root: Path,
    manifest_path: Path | None = None,
    required_paths: frozenset[str] = REQUIRED_STRATEGY_ARTIFACTS,
) -> StrategyIntegrityResult:
    """Verify runtime strategy artifacts against the committed proof manifest.

    The check reads files from disk and compares them to the SHA-256 and size
    recorded in `proof_manifest.generated.json`. It does not trust agent-reported
    values, CLI output, or cached state.
    """
    root = repo_root.resolve()
    manifest = manifest_path or root / "data" / "demo" / "proof_manifest.generated.json"
    raw, load_failure = _load_manifest(manifest)
    if load_failure is not None or raw is None:
        return StrategyIntegrityResult(
            ok=False,
            manifest_path=manifest.as_posix(),
            checked_paths=[],
            failures=[load_failure] if load_failure else [],
        )

    artifacts_by_path: dict[str, dict[str, Any]] = {}
    for item in raw.get("artifacts", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            artifacts_by_path[item["path"]] = item

    checked_paths: list[str] = []
    failures: list[StrategyIntegrityFailure] = []
    for rel_path in sorted(required_paths):
        entry = artifacts_by_path.get(rel_path)
        if entry is None:
            failures.append(
                StrategyIntegrityFailure(path=rel_path, reason="manifest_entry_missing")
            )
            continue

        path = root / rel_path
        if not path.exists():
            failures.append(StrategyIntegrityFailure(path=rel_path, reason="artifact_missing"))
            continue

        checked_paths.append(rel_path)
        expected_sha = str(entry.get("sha256", ""))
        actual_sha = sha256_file(path)
        expected_size_raw = entry.get("size_bytes")
        expected_size = int(expected_size_raw) if isinstance(expected_size_raw, int) else None
        actual_size = path.stat().st_size

        if expected_sha != actual_sha:
            failures.append(
                StrategyIntegrityFailure(
                    path=rel_path,
                    reason="sha256_mismatch",
                    expected_sha256=expected_sha,
                    actual_sha256=actual_sha,
                    expected_size_bytes=expected_size,
                    actual_size_bytes=actual_size,
                )
            )
            continue
        if expected_size is not None and expected_size != actual_size:
            failures.append(
                StrategyIntegrityFailure(
                    path=rel_path,
                    reason="size_mismatch",
                    expected_sha256=expected_sha,
                    actual_sha256=actual_sha,
                    expected_size_bytes=expected_size,
                    actual_size_bytes=actual_size,
                )
            )

    return StrategyIntegrityResult(
        ok=not failures,
        manifest_path=manifest.as_posix(),
        checked_paths=checked_paths,
        failures=failures,
    )
