# Hermes Runtime and Stripe Skills Alignment

AQTC is intentionally runnable in two layers:

1. **Standalone CLI / API** for deterministic judge reproduction.
2. **Hermes-native MCP server** for agent operation inside Hermes.

The CLI path keeps the hackathon demo reproducible on a fresh clone. The MCP path is the Hermes runtime integration: Hermes loads `aqtc-mcp`, discovers AQTC tools, and can run the business cycle through tool calls instead of shelling out to an opaque script.

## Hermes-native operation

Install AQTC with the MCP extra:

```bash
python -m pip install -e ".[mcp,api,live]"
```

Register the MCP server in Hermes:

```bash
hermes mcp add aqtc --command aqtc-mcp
hermes mcp test aqtc
```

Or add the equivalent config:

```yaml
mcp_servers:
  aqtc:
    command: "aqtc-mcp"
    args: []
    timeout: 120
    connect_timeout: 60
```

Then restart Hermes or run `/reload-mcp`. Hermes should expose these AQTC tools:

- `aqtc_status`
- `aqtc_run_cycle`
- `aqtc_get_provenance`
- `aqtc_get_report`
- `aqtc_get_events`

A Hermes operator can then ask the agent to run the quant company cycle, inspect provenance, audit events, and retrieve the customer report through MCP tool calls.

Local smoke:

```bash
bash scripts/hermes_native_smoke.sh
```

This verifies the AQTC MCP tool surface in a fresh Python process and, when Hermes is installed, checks whether Hermes currently has the `aqtc` MCP server enabled.

## Official Stripe Skills boundary

AQTC uses real Stripe test-mode revenue proof for the customer report:

- `AQTC_STRIPE_MODE=stripe_test`
- `STRIPE_SECRET_KEY` set
- `scripts/capture_stripe_proof.sh`
- redacted artifact: `docs/proof/stripe_test_paymentintent_redacted.json`

AQTC deliberately does **not** make the default judge demo depend on official outbound Stripe Skills, because those flows require user approval, Link eligibility, or external SaaS provisioning. That is a safety boundary, not an omission hidden from the judge.

For full Hermes + official Stripe Skills operation, install the sponsor skills in Hermes:

```bash
hermes skills install official/payments/stripe-projects
hermes skills install official/payments/mpp-agent
hermes skills install official/payments/stripe-link-cli
```

Recommended split:

| Operation | AQTC default | Official Stripe Skills path |
|-----------|--------------|-----------------------------|
| Customer report revenue | Stripe test PaymentIntent / mock ledger fallback | Keep PaymentIntent proof or add billing wrapper |
| Data/API purchase | budgeted local spend event | `stripe-link-cli` or `mpp-agent` with user approval |
| SaaS/reporting infra provisioning | pre-existing local state | `stripe-projects` |
| Judge reproducibility | deterministic local demo | optional live sponsor path |

Preflight for the official tools:

```bash
bash scripts/stripe_skills_preflight.sh
bash scripts/stripe_skills_preflight.sh --strict   # fail if optional tools are missing
```

## Honest claim to judges

The precise claim is:

> AQTC runs as a Hermes-native MCP server and exposes the quant-company business cycle as Hermes tools. Its default demo uses deterministic safe ledgers plus a real Stripe test-mode revenue proof when `STRIPE_SECRET_KEY` is set. Official Hermes Stripe Skills are the approved outbound-spend/provisioning path; AQTC does not self-approve Link/card spend in the deterministic judge demo.

This keeps the project aligned with the hackathon theme without pretending that the paper-trading demo is an uncontrolled live-spend agent.
