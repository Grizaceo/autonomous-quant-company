# Alpha Provenance

AQTC does **not** run Evolution Strategies live in the demo. Instead, it surfaces frozen Financial Lab evidence that proves where production alpha came from.

## HGAT+ES v4 production alpha

| Field | Value |
|-------|-------|
| Engine | Financial Lab |
| Model | HGAT+ES v4 |
| Algorithm | evolution_strategies |
| Genotype φ | 19 dimensions |
| Walkforward folds | 5 |
| Mean Sharpe | 3.255 |
| Positive fold ratio | 100% |
| Mean max drawdown | 0.032 |

Production config (`data/demo/production.toml`):

- `d_model`: 128
- `pop_size`: 30
- `reward_horizon`: 30
- `rollout_horizon`: 150
- `max_generations`: 50

Source artifacts:

- `data/demo/walkforward_report.json` — 5-fold walkforward summary
- `data/demo/production.toml` — canonical ES hyperparameters
- `data/demo/live_signals.jsonl` — paper-trading signal snapshot
- `data/demo/manifest.json` — frozen evidence bundle metadata

## Rejected candidate: 2019+ ensemble

| Field | Value |
|-------|-------|
| Name | 2019+ ensemble |
| Sharpe | -0.544 |
| Max drawdown | 0.486 |
| Reason | failed recent-regime robustness |

Source: `data/demo/rejected_ensemble_2019.json`

AQTC explicitly rejects this candidate during the business cycle and surfaces it in reports, CLI output, dashboard, and MCP tools.

## How to inspect

```bash
aqtc provenance
aqtc provenance --json
curl http://127.0.0.1:8010/provenance
fastmcp call src/aqtc/mcp_server.py aqtc_get_provenance --json
```

## Design principle

> ES is verifiable alpha origin/provenance, not runtime spectacle.

The demo validates pre-computed walkforward evidence, compares against a known-bad ensemble, and operates a paper portfolio — without re-training HGAT+ES on every `aqtc demo` invocation.

For *why* this architecture (heterogeneous graph, attention, and Evolution Strategies over backprop/PPO), see [WHY_HGAT_ES.md](WHY_HGAT_ES.md).
