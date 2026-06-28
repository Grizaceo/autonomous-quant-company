# Autonomous Quant Company

A Hermes-powered autonomous quantitative research company for the NVIDIA × Stripe × Nous Research Hermes Agent Accelerated Business Hackathon.

The agent runs a safe paper-trading business loop:

1. buys the data/compute it needs through a Stripe-style ledger,
2. validates strategies with Financial Lab walkforward evidence,
3. rejects unsafe strategies instead of hiding bad results,
4. requests a NemoClaw-style approval before paper execution,
5. updates a paper portfolio through a MockBroker,
6. generates a customer report, and
7. records revenue for that report.

This is not investment advice and does not execute live trades by default. It is a business-operations demo for autonomous financial research.

## Why it fits the hackathon

- **Earn:** the agent bills for generated quantitative research reports.
- **Spend:** the agent spends from a bounded budget for market data/compute.
- **Run operations:** the agent performs validation, risk review, paper execution, reporting, and ledger updates.
- **NVIDIA alignment:** Nemotron/NemoClaw integration points are explicit; P0 ships with transparent local mocks.
- **Stripe alignment:** Stripe Skills integration points are explicit; P0 ships with deterministic mock ledger and test-mode-ready adapter boundaries.

## Verified Financial Lab evidence included

The demo imports curated artifacts from the local Financial Lab:

- production walkforward: `data/demo/walkforward_report.json`
  - mean Sharpe: **3.255**
  - 5/5 folds positive
  - mean max drawdown: **0.032**
- rejected 2019+ ensemble: `data/demo/rejected_ensemble_2019.json`
  - Sharpe: **-0.544**
  - max drawdown: **0.486**
- live paper signals: `data/demo/live_signals.jsonl`
- canonical production config: `data/demo/production.toml`

The point is not to claim a magic trading bot. The point is to show an autonomous company that can test, reject, approve, operate, and monetize financial research safely.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest -q
aqtc demo
```

Expected demo output includes:

```text
AQTC Daily Cycle Complete
Strategy accepted: True
Rejected unsafe ensemble: True
Approval: approved
Net operating result: $17.00
```

## Commands

```bash
aqtc demo              # run deterministic business cycle
aqtc demo --json       # machine-readable result
aqtc status            # local state/event ledger
aqtc report --out demo_report.md
```

## Safety defaults

- live trading is disabled by default (`AQTC_LIVE_TRADING=false`)
- daily spend budget defaults to `$25`
- paper MockBroker only in P0
- risk guard caps gross exposure at 4.0 in the demo cycle
- bad ensemble evidence is shown and rejected

## Roadmap

- P0: deterministic local demo, tests, curated Financial Lab artifacts.
- P1: Stripe test-mode adapter, official Hermes Stripe Skills docs, Nemotron live adapter if credentials are available.
- P2: dashboard lite + Docker compose + MCP server.
- P3: public readiness, video script, submission assets.
