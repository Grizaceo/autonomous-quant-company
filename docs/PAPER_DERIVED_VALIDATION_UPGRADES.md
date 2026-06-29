# Paper-derived validation upgrades before presentation

Veredicto: sí conviene sumar esta utilidad documental antes de presentar AQTC, pero NO conviene cambiar el claim principal ni añadir métricas no ejecutadas. Los papers del sweep 2026-06-29 sirven como roadmap de validación científica post-demo, no como evidencia nueva del Sharpe 3.255.

## Qué cambia para AQTC

AQTC ya tiene un buen núcleo de integridad científica:

- candidato aceptado: HGAT+ES v4, Sharpe 3.255, 5/5 folds, MaxDD 0.032;
- candidato rechazado: 2019+ ensemble, Sharpe -0.544, MaxDD 0.486;
- evidencia congelada y hash-addressed bajo `data/demo/`;
- superficies: CLI, MCP, API, dashboard y reporte.

Los papers revisados agregan el siguiente nivel de rigor, pero todavía no están ejecutados localmente. Por eso deben vivir aquí como roadmap técnico honesto.

## Paper → utilidad concreta

| Paper | Utilidad para AQTC | Estado correcto |
|---|---|---|
| Sheppert 2026, GT-Score | Futuro criterio anti-overfit para seleccionar estrategias: `μ · ln(z) · r² / σd`; útil para demostrar mejor generalization ratio. | Roadmap. No afirmar que validó v4 todavía. |
| Nikolopoulos 2026, Spurious Predictability | Falsification audit suite: white noise, regime-switching volatility, bid-ask bounce, factor-null, GARCH; métricas `∆Z`, `Keff`, `BIF`. | Próximo gate científico de Financial Lab. |
| THGNN 2026 | Arquitectura v5: reemplazar aristas/correlaciones rolling por predicciones forward-looking en Fisher-z. | Investigación futura; no tocar demo. |
| Ozechi 2026 | Benchmark narrativo contra MVO, Equal Weight, 60/40, DRL y Transformer+GNN. | Contexto/SOTA; evidencia débil por inconsistencias. |

## Qué NO decir en la presentación

No decir:

- “AQTC ya pasó la null-suite de Nikolopoulos.”
- “GT-Score valida nuestro Sharpe 3.255.”
- “THGNN mejora nuestro HGAT actual.”
- “Ozechi prueba que nuestro enfoque es SOTA.”

Eso todavía no está corrido en nuestro repo. Decirlo sería inflar el demo. Vendedor de humo con gráficos; hay demasiados de esos.

## Qué SÍ decir si preguntan por siguiente nivel de rigor

Frase defendible:

> “El demo actual prueba lo que está en el repo: 5-fold walkforward y rechazo explícito de un candidato malo. Después de revisar literatura 2026, el siguiente gate ya está definido: GT-Score para model selection y una suite de falsificación sintética tipo Nikolopoulos. No lo metimos como claim porque aún no está ejecutado; está documentado como próximo paso verificable.”

## Utilidad pre-presentación recomendada

Mantener esta superficie como un anexo técnico:

- `docs/PAPER_DERIVED_VALIDATION_UPGRADES.md` — este archivo.
- `docs/SUBMISSION_CHECKLIST.md` debe recordar que el roadmap existe y que no se deben filtrar claims no ejecutados.

No cambiar:

- `README.md` — el producto ya tiene el mensaje correcto.
- `docs/JUDGE_ONE_PAGER.md` — debe seguir siendo simple: accepted/rejected/net/safety.
- `docs/SUBMISSION_WRITEUP.md` — copy externo debe vender el demo real, no promesas futuras.

## Backlog recomendado después de presentar

| Prioridad | Repo | Entregable |
|---|---|---|
| P0 | financial-lab | `falsification_audit/` con cinco null environments y reporte PASS/FAIL. |
| P1 | financial-lab | `robust_metrics.py` con GT-Score + ablation Sortino vs GT-Score. |
| P2 | financial-lab | Benchmark pack MVO / Equal Weight / 60-40 / DRL bajo mismos splits. |
| P3 | financial-lab | THGNN-lite edge forecaster para correlaciones 10d forward. |
| P4 | autonomous-quant-company | Importar artefactos P0/P1 como `data/demo/scientific_audit_v2/` y exponerlos en provenance v2. |

## Decisión final

Para el cierre de presentación: sumar este roadmap, no más. La historia fuerte sigue siendo:

> No prompt trading. Evolved alpha, audited operations. From evolved alpha to invoice.
