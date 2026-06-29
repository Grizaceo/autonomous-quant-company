# AQTC proof artifacts

Sanitized, judge-safe evidence files. No secrets are stored here.

## Stripe test PaymentIntent

Mock mode is the default. To generate a real Stripe **test-mode** revenue proof:

```bash
export STRIPE_SECRET_KEY=sk_test_...
bash scripts/capture_stripe_proof.sh
python scripts/generate_proof_manifest.py
```

This writes `stripe_test_paymentintent_redacted.json` with:

- `status` (expect `succeeded` when the key is valid)
- `amount_usd` and `currency`
- `external_id` (PaymentIntent id)
- `mode`: `stripe_test`
- `timestamp`

If `STRIPE_SECRET_KEY` is unset, the demo remains on the mock ledger (`$2` spend, `$19` earn, `$17` net).

## Committed example

A redacted **succeeded** Stripe test PaymentIntent proof is checked in at `stripe_test_paymentintent_redacted.json` for judges (no secrets).
