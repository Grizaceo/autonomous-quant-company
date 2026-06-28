# Architecture

Autonomous Quant Company separates the financial model from the business operator.

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
  │    └─ Local NemoClaw-style approval policy
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
