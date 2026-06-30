# INFORME CONSOLIDADO + BRAINSTORMING
## AQTC — Estado competitivo y plan de acción
### Deadline: 30 junio 2026, 23:59

**Fecha informe**: 29 junio 2026
**Fuentes revisadas**: autonomous-quant-company (28 .py, 5 docs, state files) + competitive-analysis (26 notas)

---

## PARTE A: ESTADO ACTUAL DE AQTC

### Lo que funciona (verificado)

| Componente | Estado | Evidencia |
|------------|--------|-----------|
| CLI (`aqtc demo/status/provenance/report/regime`) | ✅ Funcional | 8 tests pasando, cli.py 194 líneas |
| Business cycle completo | ✅ Funcional | 9 eventos en events.jsonl, net $17 |
| Mock Stripe ledger | ✅ Funcional | spend $2, earn $19, mock_recorded |
| Provenance CLI + JSON | ✅ Funcional | `aqtc provenance --json` retorna HGAT+ES v4 |
| MCP server (5 tools) | ✅ Funcional | aqtc_status, aqtc_run_cycle, aqtc_get_provenance, aqtc_get_report, aqtc_get_events |
| FastAPI dashboard | ✅ Funcional | /health, /status, /provenance, /cycle/run, / |
| Risk guard + policy gate | ✅ Funcional | live_broker_execution denied, max_gross=4.0 |
| NemoClaw adapter | ✅ Funcional | LocalPolicyApprovalAdapter |
| Walkforward evidence | ✅ Frozen | 5 folds, Sharpe 3.255, rejected -0.544 |
| Docs (README, PITCH, JUDGE_ONE_PAGER, WHY_HGAT_ES) | ✅ Completos | 4 docs principales + proof manifest |

### Lo que NO está implementado aún

| Componente | Estado | Impacto competitivo |
|------------|--------|---------------------|
| Telegram integration | ❌ Ausente | ALTO — SOLVENT lo tiene |
| Landing page pública | ❌ Solo GitHub README | ALTO — primer contacto visual |
| Demo video final | ⚠️ En progreso (clips + voice en modified) | ALTO — required para submission |
| Docker compose working | ⚠️ Declarado pero sin verificar | MEDIO |
| Live Nemotron (real API call) | ❌ Solo mock | MEDIO — NVIDIA pilar |
| Stripe test-mode real | ⚠️ Script existe, sin STRIPE_SECRET_KEY | MEDIO — Stripe pilar |
| Multi-seed dispersion | ❌ Solo seed=42 | BAJO para hackathon, ALTO para credibilidad |
| Non-overlapping walkforward | ❌ Solo 2012-2013 window | BAJO para hackathon |
| `SUBMISSION_WRITEUP.md` | ⚠️ Modified, uncommitted | RIESGO — puede perderse |

### Código: métricas

- **28 archivos .py** en src/aqtc/
- **~1,880 líneas** de código Python
- **8 tests** en test_cli.py
- **4 docs principales** + 1 WHY_HGAT_ES (210 líneas, el más técnico)
- **Git**: 10 commits recientes, todos docs/submission. Archivos modified sin commitear: SUBMISSION_WRITEUP.md, demo-video/*, cli.py, test_cli.py

---

## PARTE B: PANORAMA COMPETITIVO (resumen ejecutivo)

### Los 4 competidores reales (de ~40 visibles)

| # | Proyecto | Qué hace | Amenaza | Por qué |
|---|----------|----------|---------|---------|
| 1 | **SOLVENT** | Research briefs autofinanciados | ALTA | Mismo thesis "agent runs as business", $223 revenue, Telegram, números simples |
| 2 | **StackFund** | ETF research desk taiwanés | ALTA | Mismo thesis, import-linter firewall, Docker+OpenShell, P&L certificable |
| 3 | **Obol** | CFO OS multi-tenant | MEDIA | Stripe Treasury/Issuing reales, 4 agentes, pero no quant finance |
| 4 | **SlabClaw** | Acquisition desk (graded cards) | MEDIA | 8 smart contracts, ERC-4626, pero niche físico |

### Ventajas únicas de AQTC (nadie más tiene)

1. **Walkforward evidence frozen** — 5 folds, Sharpe 3.255, verificable con SHA-256
2. **Rejected trade documentado** — Sharpe -0.544, falsificación honesta
3. **Provenance verificable** — CLI + API + MCP, triple acceso
4. **HGAT+ES architecture** — heterogeneous graph + ES, no prompt trading
5. **CLI real** — `pip install -e .` → `aqtc demo`, no es screenshot

### Debilidades vs competencia

| Debilidad | Quién la explota | Impacto |
|-----------|-----------------|---------|
| Sin Telegram | SOLVENT (tiene) | Jueces ven demo de SOLVENT primero |
| Sin landing page | SOLVENT (telegra.ph), Obol | Primer impresión = README markdown |
| Números más complejos | SOLVENT ($223/$13/$209 es más simple) | Jueces tienen 60s por proyecto |
| Demo video no finalizado | Todos los Tier 1 | Sin video = sin votos |
| NVIDIA integration solo mock | StackFund (parcial) | Pilar NVIDIA débil |

---

## PARTE C: BRAINSTORMING — Ideas clasificadas por impacto/esfuerzo

### TIER 0: CRÍTICAS (hacer ANTES del 30 a las 23:59)

#### 1. Commit SUBMISSION_WRITEUP.md + demo-video
- **Qué**: Está modified sin commitear. Si pierdes esto, pierdes el writeup de submission.
- **Esfuerzo**: 2 minutos
- **Impacto**: CRÍTICO — es el documento que los jueces leen
- **Riesgo**: Ninguno

#### 2. Demo video final (60-90s)
- **Qué**: Los clips y voice ya están en modified. Falta composición final.
- **Esfuerzo**: 1-2 horas (compose.sh ya existe)
- **Impacto**: CRÍTICO — sin video no hay votos
- **Script sugerido** (del competitive analysis):
  - 0:00-0:10 — Problema: "prompt trading vs alpha evolucionado"
  - 0:10-0:25 — `aqtc demo` real corriendo
  - 0:25-0:40 — Dashboard + provenance API
  - 0:40-0:55 — Stripe $19 revenue
  - 0:55-1:00 — "From evolved alpha to invoice"

#### 3. Landing page pública (1 hora)
- **Qué**: Una página HTML estática con: headline, 3 métricas clave, demo video embed, link a GitHub.
- **Opciones**:
  - (A) GitHub Pages desde docs/ — cero costo, 30 min
  - (B) here.now skill — publica en {slug}.here.now, 45 min
  - (C) Render static site — más profesional, 1 hora
- **Recomendación**: GitHub Pages. Es gratis, permanente, y los jueces ya están en GitHub.
- **Contenido mínimo**:
  - "No es prompt trading. Es alpha evolucionado."
  - Sharpe 3.255 | 5/5 folds | Rejected -0.544
  - Video embed
  - `pip install` + `aqtc demo`
  - Link a GitHub repo

#### 4. Simplificar los números para el pitch
- **Qué**: SOLVENT dice "$223 revenue, $13 cost, $209 profit". Tú dices "spend $2, earn $19, net $17". Pero también hablas de Sharpe 3.255, 5 folds, MaxDD 0.032, 19D genotype...
- **Propuesta**: Crear un "slide card" de 4 números:
  1. **Alpha**: Sharpe 3.255 (5/5 folds)
  2. **Honestidad**: Rechazado Sharpe -0.544
  3. **Negocio**: $19 revenue, $2 cost, $17 profit
  4. **Integridad**: Provenance verificable (SHA-256)

### TIER 1: ALTO IMPACTO (si alcanza el tiempo)

#### 5. Telegram bot para demo interactiva
- **Qué**: Un bot que responde `/run_cycle` y muestra el resultado. SOLVENT ya lo tiene.
- **Esfuerzo**: 2-3 horas
- **Impacto**: ALTO — permite a jueces interactuar sin instalar nada
- **Skill relevante**: `voice-call` o directamente python-telegram-bot
- **Implementación**:
  - Reutilizar `AutonomousQuantCompanyAgent` existente
  - Bot responde: /run_cycle, /provenance, /status
  - Formatea output para Telegram (sin markdown heavy)

#### 6. Reforzar pilar NVIDIA (live Nemotron call)
- **Qué**: En vez de mock, hacer 1 llamada real a OpenRouter/NVIDIA NIM con `--nvidia-mode openrouter`
- **Esfuerzo**: 30 min (ya está el adapter, solo falta API key en CI)
- **Impacto**: MEDIO-ALTO — cierra el gap del pilar NVIDIA
- **Riesgo**: Bajo — el adapter ya soporta OpenRouter

#### 7. Stripe test-mode real en demo
- **Qué**: Ejecutar `aqtc demo --stripe-mode stripe_test` con STRIPE_SECRET_KEY real
- **Esfuerzo**: 15 min (script capture_stripe_proof.sh ya existe)
- **Impacto**: MEDIO — PaymentIntent real > mock ledger
- **Riesgo**: Bajo — test-mode no cobra dinero real

#### 8. "vs SOLVENT" comparison card
- **Qué**: Una tabla comparativa directa en el README o landing page
- **Contenido**:
  ```
  | | SOLVENT | AQTC |
  |---|---|---|
  | Alpha origin | LLM-generated | HGAT+ES v4 walkforward |
  | Validation | 1 declined job | 5-fold OOS + rejected ensemble |
  | Revenue | $223 research briefs | $19 quant report |
  | Proof | Telegram screenshot | SHA-256 frozen artifacts |
  | CLI | solvent | aqtc (pip install) |
  ```
- **Esfuerzo**: 20 min
- **Impacto**: ALTO — jueces comparan proyectos

### TIER 2: NICE-TO-HAVE (si sobra tiempo)

#### 9. Judge smoke script mejorado
- **Qué**: `scripts/judge_smoke.sh` que corre demo + muestra provenance + abre dashboard
- **Esfuerzo**: 30 min
- **Impacto**: MEDIO — facilita la vida del juez

#### 10. Docker compose funcional verificado
- **Qué**: Verificar que `docker compose up demo` realmente funciona
- **Esfuerzo**: 1 hora (debug Dockerfile + compose)
- **Impacto**: MEDIO — algunos jueces prefieren Docker

#### 11. Hash-chained event log
- **Qué**: Cada evento tiene hash del anterior (como Cortex Governor)
- **Esfuerzo**: 1-2 horas
- **Impacto**: BAJO — pero suena bien en pitch ("tamper-evident log")

#### 12. Multi-language README (中文 como StackFund)
- **Qué**: README en inglés + chino para llegar a más jueces
- **Esfuerzo**: 30 min con LLM
- **Impacto**: BAJO

---

## PARTE D: PLAN DE EJECUCIÓN (orden recomendado)

### Fase 1: CRÍTICO (hoy 29 junio, noche)
1. ✅ Commit SUBMISSION_WRITEUP.md + demo-video assets
2. Componer demo video final (compose.sh)
3. Verificar que `aqtc demo` corre limpio

### Fase 2: ALTO IMPACTO (30 junio, mañana)
4. Landing page en GitHub Pages
5. "vs SOLVENT" comparison card en README
6. Simplificar pitch numbers (slide card)

### Fase 3: SI ALCANZA (30 junio, tarde)
7. Telegram bot (si hay 2-3h libres)
8. Live Nemotron call (30 min)
9. Stripe test-mode real (15 min)

### Fase 4: POLISH (30 junio, noche)
10. Judge smoke script
11. Docker verify
12. Final commit + push

---

## PARTE E: RIESGOS IDENTIFICADOS

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Demo video no listo | MEDIA | CRÍTICO | compose.sh ya existe, priorizar |
| SUBMISSION_WRITEUP pierde cambios | ALTA | ALTO | Commit AHORA |
| Jueces no instalan pip | ALTA | MEDIO | Landing page con video + GIF |
| SOLVENT tiene demo más simple | ALTA | MEDIO | Lead con "rejected trade" (nadie lo tiene) |
| StackFund tiene misma thesis | MEDIA | MEDIO | AQTC tiene walkforward, ellos no |
| NVIDIA pilar débil | MEDIA | BAJO | 1 llamada OpenRouter lo cierra |

---

## PARTE F: MÉTRICAS DE ÉXITO (qué define "ganar")

1. **Video listo y publicado** — antes del deadline
2. **Landing page live** — con video + 4 números
3. **3 pilares demostrables** — Hermes (CLI+MCP), Stripe (test-mode), NVIDIA (1 live call)
4. **Pitch clarity** — "No es prompt trading" en <10 segundos
5. **Competitive differentiation** — "rejected trade" como headline, no como footnote

---

*Generado por DAVI, 29 junio 2026. Fuentes: autonomous-quant-company (full code review) + competitive-analysis (26 notas). Sin ediciones a ningún archivo.*
