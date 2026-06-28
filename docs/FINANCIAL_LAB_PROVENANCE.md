# Financial Lab Provenance

Curated P0 artifacts came from the local `financial-lab` repository after verification.

Included:

- `walkforward_report.json` from `experiments/results/walkforward_pop_30/`
- `rejected_ensemble_2019.json` from `experiments/results/ensemble_production.json`
- `live_signals.jsonl` from `experiments/results/live_signals/signals.jsonl`
- `production.toml` from `configs/production.toml`
- Tool Harness package from `src/financial_lab/tool_harness/`

Local source verification before import:

- Financial Lab selected tests: 210 passed, 8 warnings.
- Tool Harness import/build smoke passed.
- LabHub FinancialPlugin showed real source mode and 5 walkforward folds.
