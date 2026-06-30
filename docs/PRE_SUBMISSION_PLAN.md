# PLAN PRE-SUBMISSION — AQTC
## Branch: `feat/pre-submission-hardening`
## Objetivo: llevar AQTC de "hackathon demo" a "production-grade submission"
## Evita archivos del cursor agent (docs principales, base.py, judge_smoke.sh)

---

## FASE 0: BACKUP (5 min)
### M0.1 — Commit assets en riesgo

Archivos modified sin commitear que pueden perderse:

```
git stash push -m "WIP: demo-video + submission + cli changes"
git checkout -b feat/pre-submission-hardening
git stash pop
git add docs/demo-video/ docs/SUBMISSION_WRITEUP.md
git commit -m "feat(submission): backup demo-video assets + writeup"
```

**NO tocar**: cli.py, test_cli.py (quedan staged para después)

---

## FASE 1: TEST SUITE DE PRODUCCIÓN (3-4h)
### Objetivo: subir de 53 tests a ~120 tests, cobertura >85%

#### M1.1 — tests/test_events.py (NUEVO — 0% cobertura hoy)

```python
# EventLog: append, read, persistence, hash-chain (si se agrega)
test_event_append_and_read
test_event_persistence_across_instances
test_event_fields_present  # actor, action, summary, timestamp, evidence
test_event_json_serializable
test_event_empty_log_returns_empty_list
test_event_ordering_is_chronological
```

#### M1.2 — tests/test_signals.py (NUEVO — signals.py sin tests dedicados)

```python
# TradingSignal, PositionSignal, cap_signal, load_latest_signal
test_cap_signal_reduces_gross_to_max
test_cap_signal_preserves_relative_weights
test_cap_signal_no_change_when_under_max
test_cap_signal_with_zero_positions
test_load_latest_signal_from_jsonl
test_load_latest_signal_empty_file_raises
test_trading_signal_dataclass_fields
test_position_signal_dataclass_fields
```

#### M1.3 — tests/test_portfolio.py (NUEVO — portfolio.py sin tests dedicados)

```python
# MockBroker: rebalance, load, persistence
test_broker_rebalance_creates_positions
test_broker_rebalance_respects_weights
test_broker_load_returns_empty_initially
test_broker_persistence_across_instances
test_broker_rebalance_empty_signal
test_broker_position_count_matches_signal
test_broker_gross_exposure_capped
```

#### M1.4 — tests/test_config_extended.py (NUEVO — solo 2 tests hoy)

```python
# AQTCConfig: todos los campos, defaults, env overrides
test_config_default_values
test_config_stripe_mode_override
test_config_nvidia_mode_override
test_config_live_trading_override
test_config_auto_approve_spend_override
test_config_report_price_override
test_config_data_purchase_override
test_config_approval_policy_path_override
test_config_ensure_state_creates_dir
test_config_demo_data_dir_exists
test_config_custom_state_dir
```

#### M1.5 — tests/test_secrets.py (NUEVO — secrets.py sin tests)

```python
# get_secret: env vars, file fallback, priority
test_get_secret_from_env_var
test_get_secret_from_file
test_get_secret_env_overrides_file
test_get_secret_missing_returns_none
test_get_secret_empty_string_returns_none
test_disable_hermes_env_flag
```

#### M1.6 — tests/test_validation_extended.py (EXPAND — solo 3 tests hoy)

```python
# validation.py: edge cases, malformed data, boundary conditions
test_gate4_rejects_zero_sharpe
test_gate4_rejects_negative_folds
test_gate4_accepts_boundary_sharpe  # exact threshold
test_compare_candidate_equal_strategies
test_compare_candidate_reversed_order
test_load_json_missing_file_raises
test_load_json_invalid_json_raises
test_walkforward_report_structure_validates
test_rejected_ensemble_structure_validates
```

#### M1.7 — tests/test_business_cycle_extended.py (EXPAND — solo 1 test hoy)

```python
# Business cycle: todos los paths, edge cases, error handling
test_cycle_with_mock_stripe
test_cycle_with_stripe_test_mode
test_cycle_with_live_trading_blocked
test_cycle_report_contains_all_sections
test_cycle_report_contains_accepted_metrics
test_cycle_report_contains_rejected_metrics
test_cycle_report_contains_revenue_proof
test_cycle_report_contains_not_investment_advice
test_cycle_reset_clears_events
test_cycle_reset_clears_ledger
test_cycle_reset_clears_portfolio
test_cycle_multiple_sequential_produce_consistent_results
test_cycle_with_auto_approve_spend
test_cycle_without_auto_approve_spend
test_cycle_result_to_dict_roundtrip
test_cycle_result_json_serializable
test_cycle_nemotron_provider_recorded
test_cycle_gross_exposure_within_policy
```

#### M1.8 — tests/test_risk_guards_extended.py (EXPAND — solo 3 tests hoy)

```python
# RiskGuard: all policy combinations, edge cases
test_risk_allows_within_gross_limit
test_risk_blocks_exceeding_max_active_positions
test_risk_blocks_single_position_too_large
test_risk_allows_empty_signal
test_risk_policy_defaults
test_risk_assessment_dataclass_fields
test_cap_signal_reduces_proportionally
test_cap_signal_with_single_position
test_risk_with_all_zero_weights
test_risk_with_very_small_exposure
test_risk_with_exactly_at_limit
```

#### M1.9 — tests/test_stripe_extended.py (EXPAND — solo 2 tests hoy)

```python
# Stripe: all modes, ledger operations, edge cases
test_ledger_spend_and_earn
test_ledger_net_calculation
test_ledger_empty_returns_zero
test_ledger_multiple_operations
test_ledger_persistence_across_instances
test_mock_adapter_spend_records_event
test_mock_adapter_earn_records_event
test_mock_adapter_budget_guard_exact_limit
test_mock_adapter_budget_guard_zero_budget
test_mock_adapter_mode_is_mock
test_stripe_test_mode_adapter_mode
test_stripe_adapter_factory_mock
test_stripe_adapter_factory_stripe_test
```

#### M1.10 — tests/test_mcp_server_extended.py (EXPAND — solo 5 tests hoy)

```python
# MCP server: all tools, error states, edge cases
test_mcp_status_after_fresh_init
test_mcp_run_cycle_reset_flag_false
test_mcp_get_provenance_structure
test_mcp_get_report_with_run_flag
test_mcp_get_events_after_cycle
test_mcp_get_events_empty
test_mcp_agent_singleton_behavior
test_mcp_reset_agent_clears_instance
test_mcp_tool_registration_count
```

#### M1.11 — tests/test_integration_cli.py (NUEVO — integration test)

```python
# Full CLI integration: demo + provenance + status + report
test_cli_demo_json_output_valid
test_cli_demo_human_output_contains_decisions
test_cli_provenance_json_matches_data
test_cli_provenance_human_readable
test_cli_status_after_demo
test_cli_report_run_and_copy
test_cli_regime_mock_mode
test_cli_demo_with_stripe_test_mode
test_cli_demo_with_auto_approve
test_cli_demo_accepts_known_good_strategy
test_cli_demo_rejects_known_bad_strategy
```

#### M1.12 — tests/test_proof_manifest.py (NUEVO — verificación SHA-256)

```python
# Proof manifest: hash verification, artifact presence
test_proof_manifest_loads
test_proof_manifest_has_all_artifacts
test_proof_manifest_hashes_match_files
test_proof_manifest_model_is_hgat_es_v4
test_walkforward_report_json_valid
test_production_toml_valid
test_rejected_ensemble_json_valid
```

### Coverage target por módulo:

| Módulo | Tests hoy | Target | Archivo |
|--------|:---------:|:------:|---------|
| events.py | 0 | 8 | test_events.py |
| signals.py | 0 | 8 | test_signals.py |
| portfolio.py | 0 | 7 | test_portfolio.py |
| config.py | 2 | 12 | test_config_extended.py |
| secrets.py | 0 | 6 | test_secrets.py |
| validation.py | 3 | 12 | test_validation_extended.py |
| business_cycle.py | 1 | 18 | test_business_cycle_extended.py |
| risk.py | 3 | 11 | test_risk_guards_extended.py |
| stripe_skills.py | 2 | 13 | test_stripe_extended.py |
| mcp_server.py | 5 | 9 | test_mcp_server_extended.py |
| cli.py | 9 | 11 | test_integration_cli.py |
| proof manifest | 0 | 7 | test_proof_manifest.py |
| **TOTAL** | **53** | **~128** | |

---

## FASE 2: FEATURES COMPETITIVAS (2h)

#### M2.1 — Landing page (archivos nuevos, 0 conflicto)

`docs/landing/index.html` — single-file HTML, dark theme, zero JS:
- Hero: "No es prompt trading. Es alpha evolucionado."
- 4 metric cards: Sharpe 3.255 | 5/5 folds | Rejected -0.544 | Net $17
- Code block: `pip install -e . && aqtc demo`
- Link a GitHub + video
- Responsive, system-ui font

`docs/landing/style.css` — minimal CSS

#### M2.2 — Comparison card (archivo nuevo)

`docs/VS_COMPARISON.md` — tabla SOLVENT vs AQTC vs StackFund:
- Alpha origin, validation, revenue model, proof, CLI, tests, domain
- Honest: qué tiene cada uno que los otros no

#### M2.3 — Competitive report (ya existe, solo reference)

`docs/COMPETITIVE_REPORT_AND_BRAINSTORM.md` — ya creado, referenciar desde VS_COMPARISON.md

---

## FASE 3: HARDENING (1h)

#### M3.1 — Hash-chained event log

Modificar `src/aqtc/events.py`:
- Cada evento incluye `prev_hash` y `hash` (SHA-256)
- `verify_chain()` valida integridad completa
- Backward compatible: eventos sin hash se tratan como legacy
- Agregar tests en test_events.py

#### M3.2 — Judge smoke v2 (archivo NUEVO)

`scripts/judge_smoke_v2.sh` — NO tocar judge_smoke.sh:
- Corre demo + provenance + status + test suite
- Output limpio para jueces
- Exit code 0 = PASS

---

## ORDEN DE EJECUCIÓN

```
M0.1  (backup)              → 5 min
M1.1  (test_events)         → 20 min
M1.2  (test_signals)        → 20 min
M1.3  (test_portfolio)      → 20 min
M1.4  (test_config_ext)     → 15 min
M1.5  (test_secrets)        → 15 min
M1.6  (test_validation_ext) → 20 min
M1.7  (test_biz_cycle_ext)  → 30 min
M1.8  (test_risk_ext)       → 20 min
M1.9  (test_stripe_ext)     → 20 min
M1.10 (test_mcp_ext)        → 15 min
M1.11 (test_integration)    → 20 min
M1.12 (test_proof_manifest) → 15 min
M2.1  (landing page)        → 45 min
M2.2  (comparison card)     → 20 min
M3.1  (hash-chain events)   → 45 min
M3.2  (judge smoke v2)      → 20 min
```

**Total estimado: ~6h**

---

## ARCHIVOS PROTEGIDOS (NO TOCAR)

| Archivo | Razón |
|---------|-------|
| README.md | Cursor agent |
| docs/JUDGE_ONE_PAGER.md | Cursor agent |
| docs/PITCH.md | Cursor agent |
| docs/ARCHITECTURE.md | Cursor agent |
| docs/WHY_HGAT_ES.md | Cursor agent |
| docs/ALPHA_PROVENANCE.md | Cursor agent |
| docs/EXTERNAL_SUBMISSION.md | Cursor agent |
| docs/MCP_SERVER.md | Cursor agent |
| docs/SUBMISSION_CHECKLIST.md | Cursor agent |
| docs/PAPER_DERIVED_VALIDATION_UPGRADES.md | Cursor agent |
| scripts/judge_smoke.sh | Cursor agent |
| scripts/print_external_submission.sh | Cursor agent |
| src/aqtc/financial_core/harness/base.py | Cursor agent |
| src/aqtc/cli.py | Modificado en main, commitear como backup |
| tests/test_cli.py | Modificado en main, commitear como backup |
| docs/SUBMISSION_WRITEUP.md | Commitear como backup |
| docs/demo-video/* | Commitear como backup |

## ARCHIVOS NUEVOS (sin conflicto)

- tests/test_events.py
- tests/test_signals.py
- tests/test_portfolio.py
- tests/test_config_extended.py
- tests/test_secrets.py
- tests/test_validation_extended.py
- tests/test_business_cycle_extended.py
- tests/test_risk_guards_extended.py
- tests/test_stripe_extended.py
- tests/test_mcp_server_extended.py
- tests/test_integration_cli.py
- tests/test_proof_manifest.py
- docs/landing/index.html
- docs/landing/style.css
- docs/VS_COMPARISON.md
- scripts/judge_smoke_v2.sh

## ARCHIVOS MODIFICADOS (con cuidado)

- src/aqtc/events.py (M3.1 — hash-chain, backward compatible)
