# Demo Script

**Judge screen recording (~60s target):** run `bash scripts/judge_demo_60s.sh`.

- Step 1 prints HGAT+ES provenance; step 2 runs `demo --stripe-mode stripe_test --approve-spend` and shows the **DECISIONS** block.
- With `.env` and `STRIPE_SECRET_KEY` set, expect `stripe_earn: succeeded` on the earn line; without a key, the cycle falls back to `stripe_earn: mock_recorded` (mock ledger).

**Catch:** *From evolved alpha to invoice.*

**Subtitle:** HGAT+ES alpha, Hermes operations, Stripe revenue.

---

## 0:00 Hook — Not prompt trading

> "This is not another AI trading bot. It's a micro-compañía cuantitativa: alpha evolved by Financial Lab, validated by walkforward, operated by Hermes, billed through Stripe."

Show README headline. Emphasize: **no live ES training in the demo**.

## 0:20 Alpha provenance

```bash
aqtc provenance --json
```

Highlight:

- HGAT+ES v4, 19D genotype φ
- Mean Sharpe **3.255**, 5 folds, 100% positive
- Mean max drawdown **0.032**
- Rejected 2019+ ensemble: Sharpe **-0.544**, MaxDD **0.486**

## 0:45 Run the business cycle

```bash
bash scripts/judge_demo_60s.sh   # ~60s recording (provenance + stripe_test demo)
# manual equivalent:
aqtc demo --stripe-mode stripe_test --approve-spend
aqtc demo --json                 # machine-readable
```

Show the **DECISIONS** block; with Stripe test credentials, `stripe_earn: succeeded`.

Show:

- Strategy accepted: **True**
- Unsafe ensemble rejected: **True**
- Approval: **approved**
- Net operating result: **$17.00**

## 1:15 Safety and falsification

Show risk approval, spend approval under threshold ($2 < $5), and live-trading disabled.

Point out the **rejected candidate** evidence — AQTC does not hide bad backtests.

## 1:45 Business ledger

Show Stripe-style ledger: spend $2, earn $19, net +$17.

```bash
aqtc report --out demo_report.md
# non-destructive copy of existing report
aqtc report --run --out demo_report.md
# regenerate then copy
```

Report sections: Research provenance, Rejected candidate, Business ledger.

## 2:00 Dashboard (optional)

```bash
make serve
# open http://127.0.0.1:8010/
```

Cards: Alpha provenance, Rejected strategy, Policy, Business, Report preview.

## 2:15 MCP + API (optional)

```bash
fastmcp inspect src/aqtc/mcp_server.py:mcp
fastmcp call src/aqtc/mcp_server.py aqtc_get_provenance --json
curl http://127.0.0.1:8010/provenance
```

## 2:30 Live integrations (optional)

```bash
aqtc regime --provider openrouter --json
aqtc demo --stripe-mode stripe_test --json
```

## 2:45 Close — From evolved alpha to invoice

> "Financial Lab evolved the alpha. Walkforward validated it. Hermes operates the company. Stripe records the revenue. From evolved alpha to invoice."