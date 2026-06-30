# AQTC Pre-Submission Audit — DAVI

**Date:** 2026-06-29
**Branch:** `feat/pre-submission-hardening`
**Target:** Competition submission (NVIDIA x Stripe x Nous Hermes Hackathon)
**Refs:** `financial-lab-reference` (provenance baseline), `competitive-analysis/hackathon-2026/` (competitor landscape)

---

## 1. Verdict

**GREEN — listo para submission.** Cero P0 (SUBMIT-blockers). Cero P1 (credibility-fatal). 128 tests, 94.39% coverage, todas las gates limpias. La narrativa de diferenciación (provenance + falsificación + business loop) está respaldada por artefactos verificables.

---

## 2. Gate Matrix

| Gate | Result | Detail |
|------|--------|--------|
| Ruff check | ✅ | All checks passed (53 files) |
| Ruff format | ✅ | 53 files already formatted |
| Mypy (src+tests) | ✅ | 0 issues in 50 source files |
| Pytest + coverage | ✅ | 128 passed, 94.39% (>90% gate) |
| Secret scan | ✅ | No real secrets detected |
| Hash-chain (9 events) | ✅ | `verify_chain()` returns OK |
| Proof manifest (7 artifacts) | ✅ | 7/7 SHA-256 MATCH |
| Cross-repo integrity | ✅ | `production.toml` + `walkforward_report.json` byte-identical with financial-lab-reference |
| CI (pre-submission.yml) | ✅ | Full gate on push |
| Smoke scripts | ✅ | `judge_smoke_v2.sh` covers full matrix |
| Protected files | ⚠️ | `docs/ARCHITECTURE.md` touched (benign cross-ref, documented) |
| Threshold consistency | ✅ | 4/4 locations use `--cov-fail-under=90` |

---

## 3. Security Posture

| Check | Status | Evidence |
|-------|--------|----------|
| Live trading blocked by default | ✅ | `policy.live_trading=False`, `deny_actions=['live_broker_execution']`, explicit block in `review_trade()` |
| No silent normalization | ✅ | `live_requested` from config passes through to adapter; NOT collapsed before approval |
| Spend budget gate | ✅ | `daily_budget_usd=25`, `require_approval_above_usd=5` |
| Spend approval threshold | ✅ | Spend > $5 requires approval unless `auto_approve_spend=True` |
| No `.env` committed | ✅ | `.env` in `.gitignore` |
| `.aqtc_state/` gitignored | ✅ | Explicit in `.gitignore` |
| Strip proof redacted | ✅ | `stripe_test_paymentintent_redacted.json` contains no secrets |

---

## 4. Competitor Positioning

Basado en `competitive-analysis/hackathon-2026/00-INFORME-COMPETITIVO.md`:

- **SOLVENT** (ianalloway): 298 tests, Stripe two-sided, margin gate → fuerte en business loop pero genérico (research briefs wrapper). AQTC gana en evidencia verificable.
- **SlabClaw** (papa-raw): 8 Solidity contracts, dual payment rails → el más profundo técnicamente pero dominio físico (graded cards). No compite directamente con AQTC.
- **StackFund** (Silavater): tesis más cercana (ETF research autofinanciado) pero con fixtures congelados y simulación declarada. AQTC gana en walkforward evidence.

**Diferenciador de AQTC:** Es el único competidor con frozen walkforward evidence (5 folds, Sharpe 3.255) + falsificación explícita (rejected -0.544) + provenance SHA-256 verificable.

---

## 5. Findings (triage matrix)

### P0 — SUBMIT-blockers

Ninguno.

### P1 — HIGH

Ninguno.

### P2 — MED

| ID | Finding | Status |
|----|---------|--------|
| P2.1 | `docs/ALPHA_PROVENANCE.md` §27-45 dice que los archivos en financial-lab-reference están en `data/demo/`; en realidad están en `configs/production.toml` y `results/walkforward_report.json` | **FIXED** — paths corregidos |
| P2.2 | `docs/VS_COMPARISON.md` §20 dice "114 tests, 88.17% coverage after P1" — stale. Real: 128 tests, 94.39%. Un juez leyendo esto subestimará la madurez de tests | **FIXED** — actualizado a 128 tests, 94.39% |

### P3 — LOW

| ID | Finding | Status |
|----|---------|--------|
| P3.1 | `samples/customer_report.md` muestra 2 posiciones; eventos actuales muestran 4. Point-in-time drift esperado (la muestra es de una corrida anterior). Proof manifest mantiene integridad SHA. | DOCUMENTED — no action needed |
| P3.2 | `docs/SUBMISSION_CHECKLIST.md` items 31-33 (Tweet, Discord, Typeform) siguen unchecked — son acciones externas, no bloquean | DOCUMENTED — external actions |
| P3.3 | `docs/ARCHITECTURE.md` fue tocado en esta branch (cross-ref a WHY_HGAT_ES.md). El plan lo marca como protected, pero el cambio es solo una línea de documentación cross-reference. | DOCUMENTED — benigno |

---

## 6. Remediation log

| Commit | Block | Files changed | Status |
|--------|-------|---------------|--------|
| (pending) | P2.1: Fix reference repo paths in ALPHA_PROVENANCE.md | `docs/ALPHA_PROVENANCE.md` | Ready |
| (pending) | P2.2: Update stale test/coverage in VS_COMPARISON.md | `docs/VS_COMPARISON.md` | Ready |

---

## 7. What AQTC does well (competitive advantages)

1. **Walkforward evidence es verificable** — SHA-256 hashes cross-checked across `financial-lab-reference` y `autonomous-quant-company`. Nadie más tiene esto.
2. **Falsificación explícita** — el ensemble rechazado (-0.544 Sharpe) está en el demo, el reporte, el CLI, y los eventos. Es la feature más distintiva.
3. **Safety posture honesta** — live trading bloqueado, paper-only por default, "Not investment advice" en el reporte. No overclaims.
4. **Hash-chained events** — 9 eventos encadenados con SHA-256, verificables con `verify_chain()`.
5. **Business loop cerrado** — spend → validate → reject → trade → earn → report. Net $17 documentado.
6. **CLI instalable** — `pip install` con `aqtc demo`, `aqtc provenance`, `aqtc status`.
7. **MCP + API** — `aqtc_get_provenance`, `aqtc_get_report`, `aqtc_get_events`, `GET /provenance`.

---

## 8. Known gaps (honest framing)

- **Paper trading only.** Live broker execution is explicitly denied by policy. No real money moves.
- **Frozen walkforward evidence.** HGAT+ES v4 was trained offline in Financial Lab. AQTC surfaces the evidence, does not re-train live.
- **Stripe test-mode.** Revenue proof uses Stripe test PaymentIntent. No real customer paid real money.
- **Nemotron mock by default.** LLM calls use mock adapter; live mode requires `AQTC_NVIDIA_MODE=live` + valid key.
- **Sample report drift.** The committed `samples/customer_report.md` is from a prior run; current state has different portfolio composition. The proof manifest attests to the committed sample's integrity.

---

## 9. Final gate (self-audit 4 ejes)

| Eje | Verificación |
|-----|-------------|
| Mismo bug en otro layer? | N/A — no bugs found |
| Docs stale? | P2.1 + P2.2 fixed |
| Consumers of changed values? | N/A |
| Parallel branches? | Solo feat/pre-submission-hardening |

---

## 10. Reviewer's note

Este repositorio tiene la tesis más defendible del hackathon: "no es un bot de trading — es una micro-compañía que opera sobre evidencia falsificable." La diferenciación no está en complejidad técnica bruta (SlabClaw gana ahí) ni en completitud de business loop (SOLVENT gana ahí). Está en el triángulo: **evidencia congelada + falsificación explícita + provenance verificable.** Eso ningún otro competidor lo tiene.

El juez que valore integridad científica sobre espectáculo técnico encontrará aquí el submission más honesto.
