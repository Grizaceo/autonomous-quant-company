# Submission Checklist

## Positioning

- [x] README opens with "not prompt trading / evolved alpha" headline.
- [x] `docs/ALPHA_PROVENANCE.md` documents HGAT+ES v4 evidence.
- [x] Demo script includes "From evolved alpha to invoice" close.

## Technical

- [x] `pytest -q` passes from a fresh clone.
- [x] `aqtc demo` runs in under one minute and nets $17.
- [x] `aqtc provenance --json` returns HGAT+ES walkforward metrics.
- [x] Report has Research provenance, Rejected candidate, Business ledger sections.
- [x] Dashboard shows HGAT+ES, Sharpe 3.255, rejected -0.544, net $17.
- [x] MCP exposes `aqtc_get_provenance`; API has `GET /provenance`.
- [x] No `.env` or secrets committed.
- [x] Safety page states paper-trading defaults and approval policy behavior.
- [x] Sample report committed at `samples/customer_report.md`.
- [x] CI workflow runs lint, typecheck, tests, and smoke test.
- [x] Docker compose runs demo and optional API.

## Submission assets

- [ ] Demo video 1-3 minutes (see `docs/VIDEO_SHOTLIST.md`).
- [ ] Tweet tags `@NousResearch`.
- [ ] Discord submission link posted.
- [ ] Typeform submitted.
