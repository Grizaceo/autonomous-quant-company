# Submission Checklist

## Positioning

- [x] README opens with "not prompt trading / evolved alpha" headline.
- [x] `docs/ALPHA_PROVENANCE.md` documents HGAT+ES v4 evidence.
- [x] Demo script includes "From evolved alpha to invoice" close.

## Technical

- [x] `pytest -q` passes from a fresh clone.
- [x] `aqtc demo` runs in under one minute and nets $17.
- [x] `aqtc provenance --json` returns HGAT+ES walkforward metrics.
- [x] Report has Executive summary, Research provenance, What was rejected, Business ledger, Revenue proof sections.
- [x] Dashboard shows HGAT+ES, Sharpe 3.255, rejected -0.544, net $17.
- [x] MCP exposes `aqtc_get_provenance`; API has `GET /provenance`.
- [x] No `.env` or secrets committed.
- [x] Safety page states paper-trading defaults and approval policy behavior.
- [x] Sample report committed at `samples/customer_report.md`.
- [x] CI workflow runs lint, typecheck, tests, and smoke test.
- [x] Docker compose runs demo and optional API.

## Submission assets

- [x] Judge one-pager at `docs/JUDGE_ONE_PAGER.md`.
- [x] Proof manifest at `data/demo/proof_manifest.generated.json` (`python scripts/generate_proof_manifest.py`).
- [x] Judge smoke script at `scripts/judge_smoke.sh`.
- [x] demo video `docs/demo-video/aqtc_demo.mp4`
- [x] Stripe proof `docs/proof/stripe_test_paymentintent_redacted.json`
- [ ] Tweet tags `@NousResearch` (post externally; copy in `docs/SUBMISSION_WRITEUP.md`).
- [ ] Discord submission link posted (use blurb in `docs/SUBMISSION_WRITEUP.md`).
- [ ] Typeform submitted (external).

**Note:** Tweet, Discord, and Typeform must be completed outside the repo.
