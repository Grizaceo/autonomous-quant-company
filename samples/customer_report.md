# Autonomous Quant Company Report

## Executive summary

- Production alpha: HGAT+ES v4 with mean Sharpe 3.255 across 5 walkforward folds.
- Falsification: 2019+ ensemble rejected (Sharpe -0.544).
- Operations: paper rebalance approved; net ledger result $17.00.

## What customer paid for

- Customer report: quant research deliverable billed at $19.00.
- Data procurement: $2.00 market-data sample (status: completed).

## Research provenance

- Engine: Financial Lab
- Model: HGAT+ES v4 (19D genotype)
- Algorithm: evolution_strategies
- Mean Sharpe: 3.255 (5 folds, 100% positive)
- Mean max drawdown: 0.032
- Config: d_model=128, pop_size=30, reward_horizon=30

## What was rejected

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

## Risk policy

- Policy: aqtc-hackathon-demo-v1
- Live trading: False
- Denied actions: live_broker_execution, print_payment_card_pan, commit_secret_material
- Max gross exposure: 4.0
- Daily budget: $25.00

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

## Revenue proof

- Mock ledger revenue (mock); run scripts/capture_stripe_proof.sh with STRIPE_SECRET_KEY to generate docs/proof/stripe_test_paymentintent_redacted.json

## Not investment advice

- Research and education demo only. No investment advice, no live broker execution, paper MockBroker by default.

## Next paid report due

- Next billing cycle: T+30 days from this report (demo schedule).
