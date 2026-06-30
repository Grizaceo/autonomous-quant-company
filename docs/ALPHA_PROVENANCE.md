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

**Note on language:** `production.toml`'s comments are in Spanish (original Financial Lab
research notes). They are left untranslated deliberately — translating them would change
the file's bytes and break the byte-identical SHA-256 match to
[financial-lab-reference](https://github.com/Grizaceo/financial-lab-reference) documented
below. English translation for reference: line 1 "configs/production.toml — CANONICAL
PRODUCTION CONFIGURATION"; the `[validation_metadata]` section header "VALIDATION METADATA";
and the warning comment "DO NOT USE ensemble_production (seeds 7,8,9) — fails in test window
2019+" (this is the rejected candidate documented below, kept out of the production config).

Source artifacts:

- `data/demo/walkforward_report.json` — 5-fold walkforward summary
- `data/demo/production.toml` — canonical ES hyperparameters
- `data/demo/live_signals.jsonl` — paper-trading signal snapshot
- `data/demo/manifest.json` — frozen evidence bundle metadata

## Engine source (curated reference)

The HGAT+ES engine that produced this evidence is published as a curated,
MIT-licensed reference repository — the architecture (`hgat_policy`), the
Evolution Strategies trainer (`train_es_hgat`, `es_utils`), the fitness
function (`rollout_fitness`), and the walk-forward validator
(`walkforward_hgat`) that emits `walkforward_report.json`:

- **https://github.com/Grizaceo/financial-lab-reference**

`production.toml` (at `configs/`) and `walkforward_report.json` (at `results/`)
in that repo are **byte-identical** (SHA-256 `dc8e28b2…` and `fe87aa21…`) to the
copies under `data/demo/` in this repo. Provenance moves from "trust the hash"
to "read the engine the hash points to" — same files, same hashes, independent
copy. The 20-year market data cache and vendor connectors are excluded from the
reference repo (vendor TOS); the engine code is import-coherent for inspection.

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
