# Demo Script

## 0:00 Hook

Most trading bots only produce signals. This is an autonomous quant company: it buys resources, validates strategies, rejects unsafe candidates, executes paper operations, and bills for research.

## 0:20 Run the agent

```bash
aqtc demo
# or machine-readable:
aqtc demo --json
```

Show the business cycle completing with net operating result **$17.00**.

## 0:45 Validation

Show production walkforward Sharpe 3.255 and rejected ensemble Sharpe -0.544.

## 1:15 Safety

Show risk approval, spend approval under threshold ($2 < $5), and live-trading disabled.
If spend exceeds the approval threshold, the cycle skips procurement and continues unless `--approve-spend` is set.

## 1:45 Business

Show Stripe-style ledger: spend $2, earn $19, net +$17.
`aqtc report --out demo_report.md` copies the existing report without re-running the cycle.
Use `aqtc report --run --out demo_report.md` to regenerate.

## 2:00 Live integrations (optional)

```bash
aqtc regime --provider openrouter --json
aqtc demo --stripe-mode stripe_test --json
```

Stripe test mode confirms PaymentIntents with `pm_card_visa` when `STRIPE_SECRET_KEY` is set.

## 2:15 Close

Useful, viable, and presentable: a real operations loop for autonomous financial research.

Dashboard (optional):

```bash
make serve
# open http://127.0.0.1:8010/
```
