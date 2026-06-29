#!/usr/bin/env bash
# Print copy-paste ready text for hackathon external submission steps.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_URL="https://github.com/Grizaceo/autonomous-quant-company"
VIDEO_PATH="${REPO_ROOT}/docs/demo-video/aqtc_demo.mp4"

cat <<EOF
================================================================================
AQTC EXTERNAL SUBMISSION — copy/paste checklist
Repo: ${REPO_URL}
================================================================================

[ ] 1. TWEET (≤280 chars) — tag @NousResearch

Not prompt trading — evolved HGAT+ES alpha (Sharpe 3.255, 5/5 walkforward folds). We *reject* the bad ensemble (-0.544) before we trade. Hermes runs the micro-compañía: \$2 data → validate → paper trade → \$19 report, net \$17. Stripe test PaymentIntent succeeded. @NousResearch #HermesHackathon

[ ] 2. DISCORD — post in hackathon channel

**AQTC — Autonomous Quant Company** for the Hermes hackathon. Evolved HGAT+ES alpha (Sharpe 3.255, 5-fold walkforward), explicit rejection of bad ensemble (-0.544), Hermes-operated business cycle with Stripe revenue proof, NemoClaw-compatible policy adapter, MCP + API. Demo: \`aqtc demo\` (~60s script: \`scripts/judge_demo_60s.sh\`). ${REPO_URL}

[ ] 3. TYPEFORM — submit hackathon form

- Repo URL: ${REPO_URL}
- Video file: ${VIDEO_PATH}
- Optional live re-record: bash scripts/judge_demo_60s.sh

================================================================================
After posting, mark items complete in docs/SUBMISSION_CHECKLIST.md (external section).
================================================================================
EOF
