# Video Shotlist

**Title:** From evolved alpha to invoice  
**Duration:** 2-3 minutes  
**Catch:** No es prompt trading — alpha evolucionado por Financial Lab

---

## Shot 1 — Hook (0:00-0:15)

- **Visual:** README headline on screen
- **VO:** "This isn't another AI trading bot. It's a micro-compañía cuantitativa — evolved alpha, walkforward validation, Hermes operations, Stripe revenue."

## Shot 2 — Alpha provenance (0:15-0:40)

- **Visual:** Terminal `aqtc provenance --json`
- **Highlight:** HGAT+ES v4, Sharpe 3.255, 5 folds, MaxDD 0.032
- **VO:** "Financial Lab evolved this alpha with Evolution Strategies. We don't re-train ES in the demo — we prove where alpha came from."

## Shot 3 — Falsification (0:40-0:55)

- **Visual:** Rejected ensemble metrics (-0.544 Sharpe, 0.486 MaxDD)
- **VO:** "AQTC rejects bad candidates. The 2019+ ensemble failed recent-regime robustness — and we show it."

## Shot 4 — Business cycle (0:55-1:25)

- **Visual:** `aqtc demo` output
- **Highlight:** accepted, rejected, approved, net $17.00
- **VO:** "One command runs the full business loop: procure data, validate, approve, paper-trade, bill."

## Shot 5 — Report (1:25-1:40)

- **Visual:** `aqtc report --run --out demo_report.md` + scroll report sections
- **Sections:** Research provenance, Rejected candidate, Business ledger

## Shot 6 — Dashboard (1:40-2:00)

- **Visual:** Browser `http://127.0.0.1:8010/`
- **Cards:** Alpha provenance, Rejected strategy, Policy, Business, Report preview

## Shot 7 — MCP/API (2:00-2:15) [optional]

- **Visual:** `fastmcp call ... aqtc_get_provenance --json`
- **VO:** "Hermes agents can inspect provenance and run cycles via MCP."

## Shot 8 — Close (2:15-2:30)

- **Visual:** Net $17.00 + tagline
- **VO:** "From evolved alpha to invoice. Financial Lab evolved it. Walkforward validated it. Hermes operates it. Stripe records the revenue."

---

## B-roll assets

- `data/demo/walkforward_report.json` summary
- Dashboard cards with HGAT+ES and Sharpe 3.255
- Stripe ledger events in `aqtc status`

## Do NOT show

- Live ES training (not part of demo)
- Live broker execution (disabled by policy)
