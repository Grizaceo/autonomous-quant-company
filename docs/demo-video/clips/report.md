# Autonomous Quant Company Report

## Research provenance

- Engine: Financial Lab
- Model: HGAT+ES v4 (19D genotype)
- Algorithm: evolution_strategies
- Mean Sharpe: 3.255 (5 folds, 100% positive)
- Mean max drawdown: 0.032
- Config: d_model=128, pop_size=30, reward_horizon=30

## Rejected candidate

- Name: 2019+ ensemble
- Sharpe: -0.544
- Max drawdown: 0.486
- Reason: failed recent-regime robustness
- Gate result: rejected: Sharpe -0.544, MaxDD 0.486, consistency 0%

## Strategy decision

- Accepted production strategy: True
- Reason: accepted: Sharpe 3.255, MaxDD 0.032, consistency 100%
- Sharpe delta vs rejected ensemble: 3.799
- Drawdown improvement vs rejected ensemble: 0.454

## Approval

- Status: approved
- Reason: paper rebalance within local risk policy
- Policy: aqtc-hackathon-demo-v1

## Procurement

- Spend status: completed

## Paper portfolio

- Mode: paper
- Positions: 4
- Gross exposure: 4.000

## Business ledger

- Stripe mode: mock
- Net operating result: $17.00
