#!/usr/bin/env bash
set -euo pipefail

# Fail only on real-looking secrets, not placeholder documentation such as
# STRIPE_SECRET_KEY=<your-test-key> or empty .env.example assignments.

python - <<'PY'
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
SKIP_DIRS = {
    ".git",
    ".venv",
    ".venv-devonly",
    ".venv-smoke",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    "node_modules",
    "dist",
    "build",
}

SECRET_PATTERNS = [
    re.compile(r"sk_live_[A-Za-z0-9_\-]{8,}"),
    re.compile(r"rk_live_[A-Za-z0-9_\-]{8,}"),
    re.compile(r"whsec_[A-Za-z0-9_\-]{8,}"),
    re.compile(r"nvapi-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"sk-or-v1-[A-Za-z0-9_\-]{8,}"),
]

ASSIGNMENT = re.compile(r"\b(OPENROUTER_API_KEY|STRIPE_SECRET_KEY|NVIDIA_API_KEY)\s*=\s*([^\s#]+)")
SAFE_PLACEHOLDERS = {
    "",
    "...",
    "<your-stripe-test-secret-key>",
    "<your-test-key>",
    "<your-key>",
    "<redacted>",
    "REDACTED",
}

hits: list[str] = []
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    rel_parts = set(path.relative_to(ROOT).parts)
    if rel_parts & SKIP_DIRS:
        continue
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    for lineno, line in enumerate(text.splitlines(), 1):
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                hits.append(f"{path}:{lineno}: {pattern.pattern}")
        # Ignore grep/regex documentation lines that mention assignment tokens as patterns.
        if "grep -RInE" in line or "|" in line and "OPENROUTER_API_KEY=" in line:
            continue
        for match in ASSIGNMENT.finditer(line):
            value = match.group(2).strip().strip('"').strip("'")
            if value.endswith("...") or value in SAFE_PLACEHOLDERS or value.startswith("<"):
                continue
            hits.append(f"{path}:{lineno}: non-placeholder {match.group(1)} assignment")

if hits:
    print("Potential live secrets found:", file=sys.stderr)
    for hit in hits:
        print(f"  {hit}", file=sys.stderr)
    raise SystemExit(2)

print("secret scan ok")
PY
