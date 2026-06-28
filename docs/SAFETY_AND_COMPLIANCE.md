# Safety and Compliance

This project is a hackathon demo for autonomous business operations in financial research.

It does not provide investment advice, does not custody funds, and does not execute live trades by default.

## Guardrails

- Paper trading only in P0.
- `AQTC_LIVE_TRADING=false` by default.
- MockBroker persists local paper portfolio state only.
- RiskGuard blocks excessive gross exposure, too many positions, and live trading requests when disabled.
- Stripe spend is budget capped.
- Approval layer is explicit and logged.
- Negative validation evidence is included and used.

## Why rejected evidence matters

The demo includes an ensemble that failed a 2019+ holdout window. The agent surfaces and rejects it. This is deliberate: autonomous financial systems must falsify themselves, not only report flattering backtests.
