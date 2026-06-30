# PLAN PRE-SUBMISSION HARDENING — AQTC
## Branch: `feat/pre-submission-hardening`
## Objetivo: envío antes del deadline con evidencia ejecutable, test suite productiva y cero colisión con el cursor agent

---

## 0. Auditoría del plan anterior — hallazgos

### Baseline verificado ahora

Comandos ejecutados en `feat/pre-submission-hardening`:

```bash
pytest -q --cov=aqtc --cov-report=term-missing
ruff check .
mypy src tests
```

Resultado real:

- `53 passed`
- Coverage total: `84.26%`
- `ruff check .`: clean
- `mypy src tests`: clean, 42 source files

### Problemas del plan anterior

1. **Estaba desactualizado**: Fase 0 ya se hizo en la branch.
2. **Confundía producción con cantidad de tests**: proponía subir a ~128 tests sin priorizar riesgo. Eso infla suite, no necesariamente aumenta confianza.
3. **Duplicaba tests existentes**: `test_nemotron_adapter.py` y `test_live_adapters.py` ya cubren parte del mismo adapter.
4. **No separaba suites por tipo**: unit/integration/contract/evidence/security/smoke mezcladas.
5. **No tenía gates de envío**: faltaba matriz final con comandos obligatorios.
6. **No incluía secret scan ni proof verification como gates**: crítico para envío público.
7. **No trataba `.venv-devonly/` y `.venv-smoke/`**: aparecen untracked y deben borrarse o ignorarse antes del envío.
8. **Coverage target mal calibrado**: ya estábamos en 84.26%; el objetivo final ejecutado es `>=90%`, no simplemente “más tests”.

---

## 1. Estado actual de branch

Commits ya hechos:

```text
ee7535e feat(submission): backup demo-video assets + writeup + competitive report + plan
29eb2bd feat(cli): backup cli + test_cli changes from main
```

Pendientes untracked actuales:

```text
.venv-devonly/
.venv-smoke/
docs/MODULAR_FIX_PLAN.md
```

Acción:

- `.venv-devonly/` y `.venv-smoke/`: borrar o agregar a `.gitignore` si son generadas recurrentemente.
- `docs/MODULAR_FIX_PLAN.md`: reemplazado por este plan; no commitear salvo que quieras conservarlo como histórico.

---

## 2. Regla de no-colisión con el cursor agent

### NO tocar

- `README.md`
- `docs/JUDGE_ONE_PAGER.md`
- `docs/PITCH.md`
- `docs/ARCHITECTURE.md`
- `docs/WHY_HGAT_ES.md`
- `docs/ALPHA_PROVENANCE.md`
- `docs/EXTERNAL_SUBMISSION.md`
- `docs/MCP_SERVER.md`
- `docs/SUBMISSION_CHECKLIST.md`
- `docs/PAPER_DERIVED_VALIDATION_UPGRADES.md`
- `scripts/judge_smoke.sh`
- `scripts/print_external_submission.sh`
- `src/aqtc/financial_core/harness/base.py`

### Permitido

- Archivos nuevos bajo `tests/`
- Archivos nuevos bajo `docs/landing/`
- `docs/VS_COMPARISON.md`
- `scripts/judge_smoke_v2.sh`
- `.github/workflows/pre_submission.yml` si no existe pipeline equivalente
- `src/aqtc/events.py` solo si se implementa hash-chain backward compatible
- `pyproject.toml` solo para subir threshold de coverage después de que pase la suite
- `.gitignore` solo para ignorar `.venv-devonly/` y `.venv-smoke/`

---

## 3. Estrategia de test suite de producción

No vamos por “más tests” ciegamente. Vamos por riesgo.

### Test matrix

```yaml
test_strategy:
  artifact: "AQTC hackathon submission: CLI + API + MCP + business cycle + frozen financial evidence"
  rationale: "El proyecto mueve dinero simulado/test-mode, decide trades paper, publica claims cuantitativos y será revisado por jueces externos; los riesgos principales son integridad de evidencia, seguridad por defecto, drift de outputs y fallos de integración."
  criticality: "HIGH"

  selected_types:
    - rationale: "Módulos con lógica pura: validation, risk, signals, portfolio, config, secrets, provenance; requieren branch coverage y boundary tests."
      type: "unit"
      size: "small"
      framework: "pytest"
      dependencies: []
      gate: "Gate 1"
    - rationale: "Business cycle cruza filesystem, ledger, report generation, adapter factories, FastAPI TestClient y MCP singleton; unit doubles mentirían sobre el flujo real."
      type: "integration"
      size: "medium"
      framework: "pytest + FastAPI TestClient"
      dependencies: ["tmp_path filesystem", "mock adapters", "local demo artifacts"]
      gate: "Gate 2"
    - rationale: "API/MCP/CLI son superficies públicas para jueces y Hermes; sus outputs deben mantener contrato mínimo."
      type: "contract"
      size: "medium"
      framework: "pytest schema assertions"
      dependencies: ["JSON output from CLI/API/MCP"]
      gate: "Gate 4"
    - rationale: "El envío necesita un go/no-go ejecutable por terceros: demo, provenance, status, report, tests y secret scan."
      type: "smoke"
      size: "large"
      framework: "bash + pytest + CLI"
      dependencies: ["local repo", "optional env secrets"]
      gate: "Gate 5"

  rejected_types:
    - reason: "No hay UI interactiva crítica nueva en esta branch; landing page estática no justifica Playwright antes del deadline."
      type: "e2e"
    - reason: "No se introduce parser/matemática nueva con dominio no acotado; usar Hypothesis ahora no da ROI frente a tests de evidencia/contrato."
      type: "property-based"
    - reason: "No hay componente frontend con estado; la landing estática se valida por smoke/manual visual si hay tiempo."
      type: "component"

  deliberately_skipped:
    - why: "Live trading está explícitamente fuera de scope y denegado por policy; probar broker real sería contrario al safety posture."
      what: "Pruebas contra broker real / live execution"
    - why: "Stripe/NVIDIA live dependen de secretos; deben ser smoke opcional: skip si falta secret, fail si secret existe y falla."
      what: "CI obligatoria contra servicios externos reales"
```

---

## 4. FASE P0 — Higiene y bloqueo de riesgos de envío

### P0.1 — Limpiar untracked generados

Acción:

```bash
rm -rf .venv-devonly .venv-smoke
# o si son necesarios recurrentemente:
printf '\n.venv-devonly/\n.venv-smoke/\n' >> .gitignore
```

Verificación:

```bash
git status --short
```

Criterio: no quedan venvs untracked.

---

### P0.2 — Secret scan pre-publicación

Archivo nuevo recomendado: `scripts/pre_submission_secret_scan.sh`

Patrones mínimos:

```text
sk_live_
rk_live_
whsec_
nvapi-
sk-or-v1-
OPENROUTER_API_KEY=
STRIPE_SECRET_KEY=
NVIDIA_API_KEY=
```

Comando manual:

```bash
grep -RInE '(sk_live_|rk_live_|whsec_|nvapi-|sk-or-v1-|OPENROUTER_API_KEY=|STRIPE_SECRET_KEY=|NVIDIA_API_KEY=)' \
  --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.venv-devonly --exclude-dir=.venv-smoke . || true
```

Criterio: solo placeholders/documentación segura; cero secretos reales.

---

### P0.3 — Commit por bloques, no monolito

Orden de commits recomendado:

1. `feat(test): add evidence and contract production tests`
2. `feat(test): add security and adapter production tests`
3. `feat(submission): add static landing and comparison card`
4. `feat(events): add hash-chained event log verification` (solo si queda tiempo)
5. `chore(ci): add pre-submission gate workflow`

---

## 5. FASE P1 — Suite de producción mínima obligatoria

Objetivo: no inflar a 128 tests por volumen. Objetivo real:

- Coverage total: `>=90%` después de la suite final.
- Subir especialmente módulos débiles:
  - `secrets.py`: 45% → >=90%
  - `mcp_server.py`: 74% → >=85%
  - `cli.py`: 73% → >=80% mínimo
  - `stripe_skills.py`: 81% → >=90% si se puede
- Agregar tests que detecten drift de evidencia y contratos públicos.

---

### P1.1 — Evidence/proof suite

Archivo nuevo: `tests/test_evidence_integrity.py`

Casos:

```python
test_proof_manifest_loads
test_proof_manifest_has_required_artifacts
test_proof_manifest_hashes_match_current_files
test_walkforward_report_summary_matches_claims
test_rejected_ensemble_summary_matches_claims
test_production_toml_matches_provenance_config
test_customer_report_contains_falsification_section_after_cycle
test_customer_report_contains_not_investment_advice_after_cycle
```

Riesgo cubierto:

- Drift entre claims y data/demo
- Hashes rotos
- Regressions en falsification story

Prioridad: **obligatoria antes de envío**.

---

### P1.2 — Secrets/security suite

Archivo nuevo: `tests/test_secrets_and_security.py`

Casos:

```python
test_get_secret_prefers_environment_over_file
test_get_secret_reads_key_value_file
test_get_secret_missing_returns_none
test_disable_hermes_env_blocks_host_env_fallback
test_api_cycle_requires_token_when_token_configured
test_api_cycle_allows_without_token_only_when_unconfigured
test_live_trading_request_is_blocked_by_policy
test_stripe_live_key_is_not_accepted_in_demo_mode_if_code_supports_check
```

Riesgo cubierto:

- Secret leakage/misrouting
- API write endpoint abierto con token configurado
- Live execution accidentally enabled

Prioridad: **obligatoria antes de envío**.

---

### P1.3 — Public contract suite: CLI/API/MCP

Archivo nuevo: `tests/test_public_contracts.py`

Casos:

```python
# CLI JSON contract
test_cli_demo_json_contract_keys
test_cli_provenance_json_contract_keys
test_cli_status_json_contract_keys

# API contract
test_api_status_contract_keys
test_api_provenance_contract_keys
test_api_run_cycle_contract_keys

# MCP contract
test_mcp_status_contract_keys
test_mcp_run_cycle_contract_keys
test_mcp_get_report_contract_keys
test_mcp_get_events_contract_keys
```

Riesgo cubierto:

- Jueces/scripts consumen JSON; si cambia shape, se rompe demo.
- MCP tools recargados deben seguir retornando estructura estable.

Prioridad: **obligatoria antes de envío**.

---

### P1.4 — Ledger/adapter suite

Archivo nuevo: `tests/test_ledger_and_adapters.py`

Casos:

```python
test_ledger_empty_net_zero
test_ledger_spend_decreases_net
test_ledger_earn_increases_net
test_ledger_persists_across_instances
test_mock_stripe_budget_guard_blocks_over_budget
test_mock_stripe_budget_guard_allows_exact_budget
test_adapter_factory_mock_returns_mock_adapter
test_adapter_factory_stripe_test_returns_stripe_test_adapter_without_calling_network
test_nemotron_auto_without_keys_returns_mock
test_explicit_openrouter_without_key_returns_unavailable_summary
```

Riesgo cubierto:

- Financial ledger arithmetic
- Adapter factory drift
- Optional live integrations degrade safely

Prioridad: **obligatoria antes de envío**.

---

### P1.5 — Business invariants suite

Archivo nuevo: `tests/test_business_invariants.py`

Casos:

```python
test_daily_cycle_is_deterministic_in_mock_mode
test_daily_cycle_logs_expected_actions_in_order
test_daily_cycle_spend_requires_approval_above_threshold
test_daily_cycle_auto_approve_spend_changes_net_result
test_daily_cycle_never_executes_live_broker_by_default
test_daily_cycle_portfolio_gross_exposure_within_policy
test_daily_cycle_rejects_bad_strategy_even_when_good_strategy_accepted
test_daily_cycle_result_is_json_serializable
```

Riesgo cubierto:

- The headline business loop must not drift.
- Falsification must remain visible.

Prioridad: **obligatoria antes de envío**.

---

### P1.6 — Unit gap suite for low-covered modules

Archivo nuevo: `tests/test_unit_gaps.py`

Casos mínimos:

```python
# config
test_config_defaults_are_safe
test_config_env_overrides_are_applied_at_instantiation
test_config_ensure_state_creates_state_dir

# signals
test_cap_signal_preserves_relative_weights
test_cap_signal_noop_under_limit
test_load_latest_signal_reads_last_jsonl_entry

# portfolio
test_mock_broker_initial_state
test_mock_broker_rebalance_persists_positions

# events
test_event_log_empty_read
test_event_log_append_then_read
test_event_log_persists_across_instances
```

Riesgo cubierto:

- Branches currently missed but important enough for production confidence.

Prioridad: **alta**, pero después de P1.1-P1.5.

---

## 6. FASE P2 — Competitividad visible sin tocar docs principales

### P2.1 — Static landing page

Archivos nuevos:

- `docs/landing/index.html`
- `docs/landing/style.css`

Contenido:

- Headline: `No es prompt trading. Es alpha evolucionado.`
- Metric cards:
  - `Sharpe 3.255`
  - `5/5 folds positive`
  - `Rejected -0.544`
  - `$17 net operating result`
- Section: `Why this beats prompt trading`
- Section: `Run it yourself`
- Link al video local o YouTube si existe.

No tocar `README.md`.

---

### P2.2 — Competitive comparison card

Archivo nuevo:

- `docs/VS_COMPARISON.md`

Debe comparar:

- SOLVENT
- StackFund
- SlabClaw
- AQTC

Regla: honesto. No decir que AQTC es mejor en todo.

Ejemplo de veredicto:

```text
SlabClaw gana technical depth on-chain.
SOLVENT gana completeness del business loop genérico.
StackFund es el rival más cercano por thesis.
AQTC gana scientific/provenance rigor: walkforward + rejected ensemble + SHA-256 artifacts.
```

---

## 7. FASE P3 — Hardening opcional si queda tiempo

### P3.1 — Hash-chained event log

Modificar:

- `src/aqtc/events.py`

Requisitos:

- Backward compatible con eventos antiguos sin hash.
- Cada evento nuevo incluye `prev_hash` y `hash`.
- Función `verify_chain()` devuelve estructura:

```python
{
  "ok": bool,
  "count": int,
  "first_bad_index": int | None,
  "reason": str | None,
}
```

Tests:

```python
test_event_hash_chain_verifies_clean_log
test_event_hash_chain_detects_tampering
test_event_hash_chain_accepts_legacy_entries_as_unverified_legacy
```

Solo hacer si P1 y P2 ya están verdes.

---

### P3.2 — Pre-submission smoke script v2

Archivo nuevo:

- `scripts/judge_smoke_v2.sh`

Debe correr:

```bash
python -m pytest -q
ruff check .
mypy src tests
aqtc provenance --json >/tmp/aqtc_provenance.json
aqtc demo --json >/tmp/aqtc_demo.json
aqtc status >/tmp/aqtc_status.json
python scripts/verify_demo_outputs.py  # si existe; si no, inline python
```

Debe incluir secret scan.

Exit code:

- `0`: pass
- `1`: test/lint/type/demo failure
- `2`: secret scan suspicious hit
- `3`: missing required artifact

---

### P3.3 — CI gate workflow

Archivo nuevo si no hay workflow equivalente:

- `.github/workflows/pre-submission.yml`

Jobs:

1. install `.[dev,api,mcp,live]`
2. `ruff check .`
3. `mypy src tests`
4. `pytest -q --cov=aqtc --cov-report=term-missing --cov-fail-under=90`
5. secret scan grep

No usar secrets en CI.

---

## 8. Gate final de envío

Antes de enviar, la branch debe pasar esta matriz:

```bash
# 1. Tree y branch
git branch --show-current
git status --short

# 2. Tests + coverage
pytest -q --cov=aqtc --cov-report=term-missing --cov-fail-under=90

# 3. Lint + typing
ruff check .
mypy src tests

# 4. Demo contracts
aqtc demo --json >/tmp/aqtc_demo.json
aqtc provenance --json >/tmp/aqtc_provenance.json
aqtc status >/tmp/aqtc_status.json
python - <<'PY'
import json
for path in ['/tmp/aqtc_demo.json','/tmp/aqtc_provenance.json','/tmp/aqtc_status.json']:
    json.load(open(path))
print('json ok')
PY

# 5. Secret scan
grep -RInE '(sk_live_|rk_live_|whsec_|nvapi-|sk-or-v1-|OPENROUTER_API_KEY=|STRIPE_SECRET_KEY=|NVIDIA_API_KEY=)' \
  --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.venv-devonly --exclude-dir=.venv-smoke . || true

# 6. Protected files sanity
git diff --name-only main..HEAD | grep -E '^(README.md|docs/(JUDGE_ONE_PAGER|PITCH|ARCHITECTURE|WHY_HGAT_ES|ALPHA_PROVENANCE|EXTERNAL_SUBMISSION|MCP_SERVER|SUBMISSION_CHECKLIST|PAPER_DERIVED_VALIDATION_UPGRADES)\.md|scripts/judge_smoke\.sh|scripts/print_external_submission\.sh|src/aqtc/financial_core/harness/base\.py)$' && echo 'PROTECTED FILE TOUCHED' && exit 1 || true
```

Criterios:

- `git status --short`: limpio salvo artefactos intencionales.
- `pytest`: pass.
- Coverage: >=90%.
- `ruff`: pass.
- `mypy`: pass.
- Demo JSON: parsea.
- Secret scan: no secretos reales.
- Protected files: no tocados por esta branch.

---

## 9. Orden recomendado de ejecución

```text
P0.1 limpiar untracked
P0.2 secret scan baseline
P1.1 evidence/proof suite
P1.2 secrets/security suite
P1.3 public contracts suite
P1.4 ledger/adapter suite
P1.5 business invariants suite
P1.6 unit gap suite
P2.1 landing page
P2.2 comparison card
P3.2 smoke script v2
P3.3 CI workflow
P3.1 hash-chain events (solo si queda tiempo)
Gate final de envío
```

Por qué este orden:

1. Primero integridad y seguridad.
2. Después contratos públicos.
3. Después business loop.
4. Después landing/comparación.
5. Hash-chain es valioso pero no debe desplazar tests/evidence.

---

## 10. Qué NO hacer antes del envío

- No reescribir docs principales mientras el cursor agent los toca.
- No tocar `base.py`.
- No meter live broker ni live trading.
- No prometer Stripe/NVIDIA live si no hay artifact generado.
- No agregar tests redundantes solo para subir count.
- No modificar demo video salvo bug crítico.
- No cambiar los números del pitch sin actualizar artifacts y tests.

---

## 11. Resultado esperado si se completa P0-P2

- Branch con tests productivos: ~80-95 tests, no 128 inflados.
- Coverage >=90%.
- Secrets/security gates explícitos.
- Evidence integrity machine-checked.
- CLI/API/MCP public contracts protegidos.
- Landing page estática para jueces.
- Comparison honesta vs SOLVENT/StackFund/SlabClaw.

Ese es un envío defendible: no el más grande, sino el más verificable.
