# Stripe Integration

AQTC has two Stripe surfaces:

1. **P0/P1 local ledger** — always available, deterministic, safe for video demos.
2. **Stripe test-mode revenue adapter** — creates a real Stripe test-mode PaymentIntent when `STRIPE_SECRET_KEY` is available.

Outbound spending is represented as a budgeted procurement event in P1. Real outbound payments should use the official Hermes Stripe Skills (`mpp-agent` or `stripe-link-cli`) with user approval in P2; the agent must never self-approve card/PAN usage.

## Modes

```bash
AQTC_STRIPE_MODE=mock         # deterministic local ledger
AQTC_STRIPE_MODE=stripe_test  # create test PaymentIntent for revenue when key exists
```

Run:

```bash
aqtc demo --stripe-mode stripe_test --json
```

If `STRIPE_SECRET_KEY` is absent, the adapter remains in `stripe_test` mode but falls back to ledger-only revenue events. This keeps the hackathon demo runnable without secrets.

## Secrets

The code reads secrets from:

1. process environment,
2. `AQTC_SECRETS_FILE`, if set,
3. `~/.hermes/.env`, unless `AQTC_DISABLE_HERMES_ENV=true`.

No secret values are printed or committed.

## Official Hermes Stripe Skills path

For full sponsor alignment, P2 should add wrappers/instructions for:

```bash
hermes skills install official/payments/stripe-projects
hermes skills install official/payments/mpp-agent
hermes skills install official/payments/stripe-link-cli
```

- `stripe-projects`: provision reporting/data infra.
- `mpp-agent`: pay HTTP 402 APIs.
- `stripe-link-cli`: purchase services with user-approved virtual cards/SPT.
