# AQTC Judge One-Pager

**Slide numbers:** Sharpe **3.255** (5/5 folds) · rejected **-0.544** · net **$17** · Stripe PaymentIntent **succeeded**

**vs SOLVENT:** SOLVENT sells research briefs; AQTC sells evolved alpha proven with 5-fold walkforward.

---

**Claim 1: Scientific integrity — rejects bad alpha.**  
**Evidence:** 2019+ ensemble **rejected** — Sharpe **-0.544**, max drawdown **0.486** in `data/demo/rejected_ensemble_2019.json`; surfaced in demo, report, and dashboard. AQTC falsifies before it trades.

**Claim 2: Validated alpha (not prompt trading).**  
**Evidence:** HGAT+ES v4 frozen Financial Lab walkforward in `data/demo/walkforward_report.json` — mean Sharpe **3.255**, mean max drawdown **0.032**, **5/5** folds positive (`data/demo/manifest.json`). Inspect: `aqtc provenance --json`. Why this architecture (heterogeneous graph + ES, not backprop/PPO): [`docs/WHY_HGAT_ES.md`](WHY_HGAT_ES.md). **Read the engine source** (byte-identical config + result, SHA-256): [github.com/Grizaceo/financial-lab-reference](https://github.com/Grizaceo/financial-lab-reference).

**Claim 3: Runs as a business.**  
**Evidence:** Spend **$2** (data), earn **$19** (report), net **$17**. Stripe test PaymentIntent **succeeded** — redacted proof at `docs/proof/stripe_test_paymentintent_redacted.json` (`pi_3TncGX4qsu8xWISK0x5Rc0IY`).

**Claim 4: Hermes-native agent surface.**
**Evidence:** AQTC exposes `aqtc_run_cycle`, `aqtc_status`, `aqtc_get_provenance`, `aqtc_get_report`, and `aqtc_get_events` as Hermes MCP tools via `aqtc-mcp`. `aqtc demo` prints the same DECISIONS block for fresh-clone reproducibility. Smoke: `bash scripts/hermes_native_smoke.sh`.

**Claim 5: Safe by default.**  
**Evidence:** `live_broker_execution` denied in `examples/approval_policy.yaml`; NemoClaw-compatible policy adapter (`src/aqtc/integrations/nemoclaw.py`); paper `MockBroker` only.
