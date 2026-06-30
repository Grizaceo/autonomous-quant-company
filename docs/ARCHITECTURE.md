# Architecture

Autonomous Quant Company separates the financial model from the business operator.

> Design rationale for the financial model — why a heterogeneous graph + Evolution Strategies, and what the 19D genotype encodes — is in **[WHY_HGAT_ES.md](WHY_HGAT_ES.md)**.

```text
Hermes Agent
  │
  ├─ AQTC Business Agent
  │    ├─ research / regime summary
  │    ├─ strategy validation
  │    ├─ risk approval
  │    ├─ paper execution
  │    ├─ report generation
  │    └─ billing/spend ledger
  │
  ├─ Financial Core
  │    ├─ walkforward report loader
  │    ├─ Gate4 decision logic
  │    ├─ Tool Harness genotype (19D)
  │    ├─ signal loader/capper
  │    └─ risk guard
  │
  ├─ Integrations
  │    ├─ Stripe ledger / future Stripe Skills
  │    ├─ Mock Nemotron / future NVIDIA adapter
  │    └─ NemoClaw-compatible policy adapter (local deterministic guardrails in demo)
  │
  └─ API / future MCP tools
```

## P0 scope

P0 is deterministic and safe. It proves the operating loop without requiring real keys:

- `aqtc demo` runs end-to-end.
- `pytest -q` verifies strategy acceptance, rejection, risk guardrails, mock Stripe ledger, and business cycle.
- live trading and real payments are disabled.

## P1 integration seams

- `aqtc.integrations.stripe_skills` will gain Stripe test-mode and official Hermes Stripe Skills wrappers.
- `aqtc.integrations.nvidia` will gain a live Nemotron adapter.
- `aqtc.integrations.nemoclaw` will gain external approval integration while preserving local policy fallback.


## P1 additions

- `aqtc.integrations.nvidia` supports OpenRouter, NVIDIA NIM, and OpenCode Zen via OpenAI-compatible chat completions.
- `aqtc.integrations.stripe_skills` supports mock ledger plus Stripe test-mode PaymentIntent creation for revenue.
- `examples/approval_policy.yaml` makes NemoClaw-compatible constraints explicit.
- `aqtc.mcp_server` exposes five FastMCP tools for Hermes.
