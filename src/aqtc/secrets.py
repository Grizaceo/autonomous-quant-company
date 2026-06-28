from __future__ import annotations

import os
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def get_secret(name: str, *, env_file: str | Path | None = None) -> str | None:
    """Return a secret from env, an explicit env file, or Hermes' local env file.

    The value is never printed by this module. Public users can ignore the Hermes
    fallback; it exists so local Hermes demos can use ~/.hermes/.env without
    copying secrets into this repo.
    """
    if os.getenv(name):
        return os.getenv(name)

    candidate_files: list[Path] = []
    if env_file:
        candidate_files.append(Path(env_file).expanduser())
    if os.getenv("AQTC_SECRETS_FILE"):
        candidate_files.append(Path(os.environ["AQTC_SECRETS_FILE"]).expanduser())
    if os.getenv("AQTC_DISABLE_HERMES_ENV", "false").lower() not in {"1", "true", "yes", "on"}:
        candidate_files.append(Path.home() / ".hermes" / ".env")

    for path in candidate_files:
        values = _parse_env_file(path)
        if values.get(name):
            return values[name]
    return None


def has_secret(name: str, *, env_file: str | Path | None = None) -> bool:
    return bool(get_secret(name, env_file=env_file))
