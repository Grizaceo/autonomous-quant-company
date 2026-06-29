# Autonomous Quant Company

**No es prompt trading. Es alpha evolucionado por Financial Lab, validado por walkforward, operado por Hermes como una micro-compañía cuantitativa auditable.**

*From evolved alpha to invoice.* — HGAT+ES alpha, Hermes operations, Stripe revenue.

A Hermes-powered autonomous quantitative research company for the NVIDIA × Stripe × Nous Research Hermes Agent Accelerated Business Hackathon.

## What makes this different

| Typical AI trading demo | AQTC |
|-------------------------|------|
| Prompt → signal → chart | Financial Lab **HGAT+ES v4** alpha with frozen walkforward evidence |
| Hides bad backtests | **Rejects** failed candidates (2019+ ensemble Sharpe **-0.544**) |
| No business loop | Buys data, validates, approves, paper-trades, **bills $19** via Stripe |
| Black box | Full provenance: `aqtc provenance --json`, MCP, API `/provenance` |

**Key principle:** ES is verifiable alpha origin/provenance — not heavy live training in the demo.

## Verified Financial Lab evidence

Curated artifacts under `data/demo/` — no runtime ES training:

| Metric | Accepted (HGAT+ES v4) | Rejected (2019+ ensemble) |
|--------|----------------------|---------------------------|
| Mean Sharpe | **3.255** | **-0.544** |
| Walkforward folds | 5 (100% positive) | — |
| Mean max drawdown | **0.032** | **0.486** |
| Genotype φ | 19D | — |

```bash
aqtc provenance          # human-readable provenance summary
aqtc provenance --json   # machine-readable
```

## Business loop

The agent runs a safe paper-trading business cycle:

1. buys the data/compute it needs through a Stripe-style ledger,
2. validates strategies with Financial Lab walkforward evidence,
3. rejects unsafe strategies instead of hiding bad results,
4. requests a NemoClaw-style approval before paper execution,
5. updates a paper portfolio through a MockBroker,
6. generates a customer report, and
7. records revenue for that report.

This is not investment advice and does not execute live trades by default.

## Architecture

```mermaid
flowchart TB
  CLI["aqtc CLI / MCP / FastAPI"] --> Agent["AutonomousQuantCompanyAgent"]
  Agent --> Policy["ApprovalPolicy YAML + NemoClaw adapter"]
  Agent --> Nemotron["Nemotron adapter (mock or live)"]
  Agent --> Stripe["Stripe adapter (mock or test-mode)"]
  Agent --> FinLab["Financial Lab artifacts + provenance"]
  Agent --> Broker["MockBroker (paper)"]
  Agent --> Ledger["Local state: events, ledger, report"]
  Policy -->|deny live_broker_execution| Broker
  Stripe -->|earn $19 / spend $2| Ledger
```

## Demo results (deterministic mock mode)

- Strategy accepted: **True**
- Unsafe ensemble rejected: **True**
- Trade approval: **approved** (paper rebalance)
- Ledger: spend **$2**, earn **$19**, net **$17**
- Gross exposure capped at **4.0**

**Revenue note:** mock mode records ledger entries locally. Stripe test mode creates real test PaymentIntents; when `STRIPE_SECRET_KEY` is set they are confirmed with `pm_card_visa` and logged as `succeeded`.

## Quick start

```bash
python -m pip install -e ".[dev,api,mcp,live]"
pytest -q --cov=aqtc
aqtc demo
```

Expected output includes `Net operating result: $17.00`.

Docker:

```bash
docker compose up demo
# optional API + dashboard at http://127.0.0.1:8010/
docker compose up api
```

## Commands

```bash
aqtc demo                    # run deterministic business cycle
aqtc demo --json             # machine-readable result
aqtc provenance              # Financial Lab alpha provenance
aqtc provenance --json
aqtc demo --approve-spend    # bypass human approval for large spends
aqtc status                  # local state/event ledger
aqtc report --out report.md  # copy existing report (non-destructive)
aqtc report --run --out report.md  # regenerate then copy
make serve                   # FastAPI dashboard on :8010
```

## Safety defaults

- live trading disabled (`AQTC_LIVE_TRADING=false`)
- `live_broker_execution` denied in `examples/approval_policy.yaml`
- daily budget and approval thresholds canonical in YAML (env override only when set)
- spend above threshold requires human approval unless `--approve-spend` / `AQTC_AUTO_APPROVE_SPEND`
- paper MockBroker only

See [docs/REAL_VS_MOCK.md](docs/REAL_VS_MOCK.md) and [docs/ALPHA_PROVENANCE.md](docs/ALPHA_PROVENANCE.md).

## Live quickstart (optional)

```bash
export STRIPE_SECRET_KEY=<your-stripe-test-secret-key>
aqtc demo --stripe-mode stripe_test --json

export OPENROUTER_API_KEY=...
aqtc regime --provider openrouter --json
aqtc demo --nvidia-mode openrouter --json
```

## MCP server

```bash
aqtc-mcp
fastmcp call src/aqtc/mcp_server.py aqtc_get_provenance --json
fastmcp call src/aqtc/mcp_server.py aqtc_get_report --json
```

## Development

```bash
make install-all
make lint
make typecheck
make test
make smoke
```
