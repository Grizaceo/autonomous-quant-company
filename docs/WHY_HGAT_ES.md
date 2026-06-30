# Why HGAT + Evolution Strategies

> **Scope.** This explains the *design rationale* behind the production alpha AQTC
> surfaces ("HGAT+ES v4"). Every claim traces to a file you can open. The frozen
> evidence ships in this repo; the model/optimizer source lives in the Financial
> Lab engine repo (see [FINANCIAL_LAB_PROVENANCE.md](FINANCIAL_LAB_PROVENANCE.md)).
> Inspect with `aqtc provenance --json`, `curl http://127.0.0.1:8010/provenance`,
> or the MCP tool `aqtc_get_provenance`.

## TL;DR for judges

The market is **not a single homogeneous tensor of returns** — equities are priced
by *different kinds of drivers* (sector commodities, macro rates/FX, risk factors).
So the policy is a **Heterogeneous Graph Attention network (HGAT)**: typed nodes for
`stock`, `commodity`, `macro`, `risk`, with learned attention fusing each driver's
influence onto the equities. The objective we actually care about — risk-adjusted
return *after* a turnover penalty and an attention-entropy regularizer — is
**non-differentiable and rank-based**, so we optimize it with **Evolution Strategies
(ES)**, a gradient-free black-box optimizer, instead of backprop or PPO. The result
is then **falsified, not just fitted**: a sibling candidate that looked fine
in-sample (2019+ ensemble) is *rejected* (Sharpe **−0.544**) before the accepted
model (mean Sharpe **3.255**, **5/5** positive folds) is promoted.

## 1. Why a *heterogeneous* graph (not one big network)

The implementing model is a genuine HGAT, not a stub. In the engine repo
(`financial-lab/src/financial_lab/hgat_policy.py`):

- **Four node types are first-class.** `HGATLayer` builds a separate per-type input
  projection and a per-type `nn.MultiheadAttention` for each of
  `stock`, `commodity`, `macro`, `risk`.
- **Typed edges as metapaths.** A `SemanticAttention` module fuses the metapath
  views (stock, commodity→stock, macro→stock, risk→stock) so influence flows along
  known channels into equities.

Why it matters: a flat MLP/Transformer over concatenated features treats a copper
price and a VIX print as interchangeable columns. The heterogeneous graph encodes
the *prior* that drivers are typed and connect to equities through known channels —
the inductive bias that makes a 500-day training window (`train_min=500`) enough to
generalize out-of-sample (§4).

## 2. Why attention

Attention lets the model **weight drivers per regime** instead of hard-coding a
factor loading.

- `SemanticAttention` fuses the metapath views with a **temperature-scaled softmax
  (τ=4)**, deliberately kept in the "hot" regime so no single metapath dominates
  (max metapath weight is structurally bounded to ~0.42 vs ~0.81 at τ=1), with a
  hard floor guaranteeing each metapath ≥10% weight. This prevents the controller
  from collapsing onto one factor and overfitting a single regime.
- Attention is **exposed as tunable** in the AQTC genotype: `attention_heads=4`,
  `attention_temp=1.0` (`src/aqtc/financial_core/harness/base.py:149-150`).
- Crucially, **attention diversity is part of the training objective**: ES adds
  `attention_entropy_bonus * mean_entropy` to fitness
  (`financial-lab/src/financial_lab/train_es_hgat.py`, coefficient `2.0` in
  `data/demo/production.toml`). The model is *paid* to keep attention spread out — a
  built-in anti-overfit regularizer on the fusion weights.

## 3. Why Evolution Strategies instead of backprop / PPO

This is the load-bearing choice, and it is dictated by the **shape of the
objective**, not by preference.

**The objective is non-differentiable and rank-based.** Fitness lives in
`financial-lab/src/financial_lab/rollout_fitness.py` and is composed of:

- **Sortino / Sharpe** over a *rollout* through a cost-aware trading environment
  (`lkn3_costs=true`) — a path-dependent simulation, not a closed-form differentiable
  loss;
- a **max-drawdown** penalty `− λ_dd · max(0, mdd − dd_target)` (a min-over-path
  operator);
- an **L1 turnover penalty** `− λ_to · turnover_l1(actions)` with
  `lambda_turnover = 3.0`, penalizing the *change* in realized position vectors;
- plus the **attention-entropy bonus** from §2.

None of drawdown, L1 turnover on realized trades, or ranked Sharpe over a simulated
book with transaction costs has a clean gradient back to the weights. Backprop
cannot ascend this surface directly.

**ES sidesteps the gradient entirely.** The loop in
`financial-lab/src/financial_lab/walkforward_hgat.py` is textbook OpenAI-style ES:
**antithetic noise** pairs (`θ ± σ·ε`), a per-generation **σ decay**, fitness mapped
through **`centered_ranks`** (`es_utils.py`) so only the *ordering* of candidates
matters — invariant to the objective's scale, outliers, and discontinuities — and a
weight-decayed update. The canonical run uses the **`[es]` block of
`data/demo/production.toml`**: `pop_size=30, sigma_init=0.025,
sigma_decay=0.99975, lr=0.01, weight_decay=0.005, max_generations=50,
attention_entropy_bonus=2.0, lambda_turnover=3.0` (these are the production config
values, which the training function accepts as arguments; the function's own
fallback defaults differ).

Rank-based ES is exactly the right tool when the reward has plateaus, kinks
(drawdown/turnover thresholds), and simulator noise — the regime PPO's
policy-gradient estimator handles poorly. A **full `[ppo]` block ships alongside
`[es]` in `production.toml`** (`n_envs=8, total_steps=1e6, clip=0.2,
gae_lambda=0.95`): PPO was a live, configured alternative — and ES is the one that
produced the accepted walkforward.

**ES also optimizes things backprop structurally cannot touch.** AQTC surfaces the
harness genotype **φ — a 19-dimension vector** (`HarnessGenotype.dim() == 19`,
verifiable: `src/aqtc/financial_core/harness/base.py:104-211`). φ decomposes into:

| Block | Dims | Params |
|---|---|---|
| Feature windows | 7 | RSI window 14; MACD 12/26/9; z-score window 20; PCA k=5; wavelet level 3 |
| Risk | 5 | max_gross 10; max_active 6; stop_loss 0.02; vol_target 0.15; correlation_limit 0.7 |
| Execution | 2 | participation_rate 0.1; slippage_bps 5 |
| Controller (HGAT) | 5 | d_model; n_layers 3; dropout 0.2; attention_heads 4; attention_temp 1.0 |

Several of these are **integers / configuration choices** — "use 14-day RSI vs
20-day" has no gradient. ES, being black-box, evolves continuous policy weights
**and** this mixed discrete/continuous configuration with the *same* machinery —
`"Genotype φ — ES evolves this, not raw weights"` (`base.py:109`).

> **Two ES surfaces, stated plainly.** The frozen Sharpe-3.255 walkforward evolved
> the **HGAT policy weights** (`walkforward_hgat.py`). The 19-dim **φ** above is the
> higher-level **tool/risk/execution/controller configuration** genotype AQTC
> exposes (`base.py`). Both are gradient-free for the reasons above. Note also that
> φ's controller seed default is `d_model=64` (`base.py:146`) while the *production
> run* used `d_model=128` (`data/demo/production.toml`, `provenance.py`) — 64 is the
> genotype's starting value, 128 is the config that produced the frozen evidence.

## 4. The falsification story — evidence it isn't overfit

A high in-sample Sharpe proves nothing on its own. AQTC's claim is **process**, and
the artifacts back it:

- **5-fold walkforward, out-of-sample** (`data/demo/walkforward_report.json`):
  `train_min=500, test_window=100, step_size=50`. **Mean Sharpe 3.255 ± 1.531, 5/5
  folds positive (`sharpe_consistent = 1.0`), mean MaxDD 0.032, hit rate 0.815.**
  The five per-fold Sharpes (3.43, 5.55, 0.87, 3.83, 2.60) recompute to the reported
  mean at full float precision.
- **A rejected sibling.** The 2019+ ensemble (seeds 7,8,9) is kept in the evidence
  bundle precisely *because it failed*: Sharpe **−0.544**, MaxDD **0.486**, "failed
  recent-regime robustness" (`data/demo/rejected_ensemble_2019.json`). AQTC promotes
  HGAT+ES v4 **only after** surfacing this falsified candidate in the demo, report,
  and dashboard.

Showing the model you threw away, with the metric that killed it, is the strongest
available signal that the accepted result survived genuine out-of-sample stress
rather than a lucky fit.

## 5. Honest trade-offs vs alternatives

| Architecture choice | Honest alternative | Trade-off AQTC accepts |
|---|---|---|
| **HGAT + Evolution Strategies (chosen)** | — | Slow, sample-inefficient optimization and added graph-construction complexity, in exchange for the right inductive bias (typed market drivers) and the ability to optimize a non-differentiable, rank-based, cost-aware reward end-to-end. |
| HGAT + **backprop** | Same graph, differentiable surrogate loss | Faster training, but only by replacing the real objective (Sortino/drawdown/L1-turnover λ=3.0 over a cost-aware rollout + attention-entropy bonus 2.0) with a differentiable proxy. AQTC keeps the true objective and pays with gradient-free search. |
| **Transformer** (sequence over concatenated features) | Strong temporal modeling, no typed structure | Drops the heterogeneous prior — copper price and VIX become interchangeable columns — and needs far more data than 500-day windows. |
| **PPO / deep RL** | Policy-gradient on the same env (full `[ppo]` block ships in `production.toml`) | A live, configured alternative. PPO's gradient estimator struggles with the plateaus/kinks of drawdown + L1-turnover rewards and simulator noise; rank-based ES is more robust — and PPO did not produce the accepted walkforward. |
| **LSTM** (recurrent per-asset signal) | Cheap, well-understood temporal model | No cross-asset / cross-type attention and no typed edges, so commodity/macro/risk influence on equities must be hand-engineered. |
| **Linear / classical factor model** | Maximally interpretable, low-overfit risk | Cannot represent regime-dependent, non-linear driver fusion or be co-optimized with the 19-dim genotype. Overfit risk is instead offset by 5-fold walkforward + explicit falsification of the rejected ensemble. |

## 6. Scope & limits of the evidence

We state plainly what the frozen walkforward does and does **not** establish, so the
architecture argument above is not mistaken for a production-validated track record.
The reasoning for HGAT+ES is *design-level* and holds independently; the headline
Sharpe is *research-grade*, and these are the open questions a careful reviewer
should ask.

- **The 5 folds are not 5 independent years.** `step_size=50 < test_window=100`, so
  consecutive test windows overlap 50%, and all five fall inside
  **2012-06-22 → 2013-08-16** — a single ~14-month window
  (`data/demo/walkforward_report.json`, `folds[].test_*_date`). Effective
  out-of-sample is closer to one benign regime than five independent draws;
  `std_sharpe = 1.531` across correlated folds understates true uncertainty.
- **Single seed for the accepted config.** The promoted run used `seed = 42` only
  (`production.toml`), while the *rejected* ensemble used three seeds (7, 8, 9). With
  no seed dispersion for the winner, skill and a lucky ES draw can't yet be
  separated — fold Sharpe already ranges 0.87 → 5.55.
- **Stress-regime robustness is shown only for the failure.** We reject a 2019+
  ensemble (Sharpe −0.544), but the **accepted** config is never tested on 2019+,
  COVID-2020, or 2022. The falsification proves the framework *can* fail
  out-of-regime; it does not prove the accepted model survives stress.
- **Thin, leveraged universe.** 10 IPSA names (`n_stocks = 10`) with risk genes
  capping `max_gross = 10`, `max_active = 6`. Pairing Sharpe 3.255 with MaxDD 0.032
  on a small, leveraged book is unusually clean — a reviewer should see the
  cost/financing model (commission + spread + borrow) and a look-ahead/survivorship
  check before treating it as tradable.
- **Deployed ≠ validated config.** The live snapshot in `data/demo/live_signals.jsonl`
  was generated with `d_model = 64, pop_size = 20, n_generations = 20`; the validated
  walkforward used `128 / 30 / 50`. The 3.255 result describes the validated config,
  not the one emitting the sample allocations.

**What would upgrade this from research-grade to production-validated:** (i) multi-seed
dispersion for the accepted config; (ii) non-overlapping walkforward spanning
2008 / 2020 / 2022 stress regimes *with the accepted config*; (iii) net-of-cost
comparison against equal-weight, momentum, and a linear-factor baseline over the same
windows; (iv) a deflated Sharpe / PBO accounting for the config search; (v) reconcile
the deployed (64) vs validated (128) controller. None of these change *why* HGAT+ES is
the right architecture — they are what turns a promising walkforward into a defensible
alpha.

## 7. Inspect it yourself

```bash
aqtc provenance --json                         # engine, model, 19D genotype, accepted vs rejected
cat data/demo/walkforward_report.json          # 5 folds, summary, config
cat data/demo/production.toml                  # [es] + [ppo] hyperparameters
cat data/demo/proof_manifest.generated.json    # SHA-256 of every frozen artifact
```

**Provenance anchor.** The frozen `production.toml` and `walkforward_report.json`
are **byte-identical** between this repo and the Financial Lab engine
(SHA-256 `dc8e28b2…` and `fe87aa21…`, recorded in
`data/demo/proof_manifest.generated.json`). So the evidence AQTC ships is the
literal output of the architecture described here — verifiable today without
publishing the full engine repo.
