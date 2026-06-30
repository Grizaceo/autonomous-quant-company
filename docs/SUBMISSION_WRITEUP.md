# AQTC hackathon submission copy

**Repo:** https://github.com/Grizaceo/autonomous-quant-company

## Tweet (≤280 chars)

Not prompt trading — evolved HGAT+ES alpha (Sharpe 3.255, 5/5 folds). We *reject* the bad ensemble (-0.544) before we trade. Hermes runs the micro-company: $2 data → validate → paper trade → $19 report, net $17. Stripe PaymentIntent succeeded. @NousResearch #HermesHackathon

## Thread (3 posts)

1/ AQTC is an autonomous quant *company*, not a chart bot. Financial Lab HGAT+ES v4 with frozen walkforward evidence (Sharpe 3.255, MaxDD 0.032, 5/5 folds). `aqtc provenance --json` shows the artifacts.

2/ Scientific integrity: we publish the failure — 2019+ ensemble rejected at Sharpe -0.544 / MaxDD 0.486. `aqtc demo` prints a DECISIONS block (accept/reject, spend gate, trade gate, Stripe earn).

3/ Business loop: spend $2, earn $19, net $17. Stripe test PaymentIntent succeeded (redacted proof in repo). Paper MockBroker only; live broker execution denied by policy. Repo: https://github.com/Grizaceo/autonomous-quant-company

## Discord blurb

**AQTC — Autonomous Quant Company** for the Hermes hackathon. Evolved HGAT+ES alpha (Sharpe 3.255, 5-fold walkforward), explicit rejection of bad ensemble (-0.544), Hermes-operated business cycle with Stripe revenue proof, NemoClaw-compatible policy adapter, MCP + API. Demo: `aqtc demo` (~60s script: `scripts/judge_demo_60s.sh`). https://github.com/Grizaceo/autonomous-quant-company

## Typeform / video

- **Video:** `docs/demo-video/aqtc_demo.mp4` (upload to X/Twitter with the tweet)
- **Optional re-record (live Stripe in terminal):** `bash scripts/judge_demo_60s.sh`
