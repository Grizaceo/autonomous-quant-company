# Real vs mock integrations

AQTC ships with deterministic mocks by default. Live integrations are opt-in.

## Alpha provenance vs live ES

| Surface | Behavior |
|---------|----------|
| `aqtc provenance` | Reads frozen Financial Lab artifacts from `data/demo/` |
| `aqtc demo` | Validates pre-computed walkforward evidence — **no ES training** |
| Financial Lab (offline) | HGAT+ES v4 evolution produced the artifacts |

ES is alpha **origin/provenance**, not a runtime spectacle in the demo.

| Component | Default (P0) | Live / test mode (P1) | Notes |
|-----------|--------------|------------------------|-------|
| Stripe ledger | `AQTC_STRIPE_MODE=mock` | `stripe_test` + `STRIPE_SECRET_KEY` | Test-mode `earn` confirms PaymentIntents with `pm_card_visa`; outbound spend stays a budgeted ledger event. |
| Nemotron | `AQTC_NVIDIA_MODE=mock` | `openrouter`, `nvidia`, `opencode_zen` | Explicit provider without API key returns `{provider}-unavailable` with a warning. |
| Trading | paper MockBroker | disabled | `live_broker_execution` is denied in `examples/approval_policy.yaml`. |
| Budget / approval | YAML policy | env override when set | `AQTC_DAILY_BUDGET_USD` and `AQTC_REQUIRE_APPROVAL_ABOVE_USD` override YAML only when present. |

## Environment variables

See `.env.example` for the full list. Important knobs:

- `AQTC_STATE_DIR` — isolate local state (used in tests and Docker).
- `AQTC_AUTO_APPROVE_SPEND` / `--approve-spend` — bypass human approval for large spends.
- `AQTC_OPENCODE_ZEN_BASE_URL` — OpenCode Zen OpenAI-compatible base URL.

## Revenue honesty

Mock mode records ledger events locally. Stripe test mode creates real test PaymentIntents; when confirmed they report `status=succeeded`. Without a key, test-mode adapters fall back to mock ledger entries labeled `mock_recorded`.
