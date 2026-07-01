#!/usr/bin/env bash
set -euo pipefail

strict=false
if [[ "${1:-}" == "--strict" ]]; then
  strict=true
fi

missing=0
check_cmd() {
  local name="$1"
  local hint="$2"
  if command -v "$name" >/dev/null 2>&1; then
    echo "ok: $name found ($(command -v "$name"))"
  else
    echo "missing optional: $name — $hint"
    missing=$((missing + 1))
  fi
}

if command -v hermes >/dev/null 2>&1; then
  echo "ok: hermes found ($(command -v hermes))"
  if hermes skills list 2>/dev/null | grep -qiE 'stripe|mpp'; then
    echo "ok: Hermes skills list includes Stripe/MPP-related entries"
  else
    echo "info: Stripe/MPP skills not visible in this Hermes skills list"
    echo "hint: hermes skills install official/payments/stripe-projects"
    echo "hint: hermes skills install official/payments/mpp-agent"
    echo "hint: hermes skills install official/payments/stripe-link-cli"
  fi
else
  echo "missing optional: hermes — install Hermes Agent to use official skills"
  missing=$((missing + 1))
fi

check_cmd stripe "install Stripe CLI and plugin: stripe plugin install projects"
check_cmd link-cli "install Stripe Link CLI: npm install -g @stripe/link-cli (US/Link eligibility required)"

if [[ -n "${STRIPE_SECRET_KEY:-}" ]]; then
  echo "ok: STRIPE_SECRET_KEY is set (value not printed)"
else
  echo "info: STRIPE_SECRET_KEY not set; AQTC Stripe test PaymentIntent proof will be skipped/fallback"
fi

if [[ "$strict" == true && "$missing" -gt 0 ]]; then
  echo "strict preflight failed: $missing optional sponsor tool(s) missing"
  exit 1
fi

echo "stripe skills preflight complete (missing_optional=$missing, strict=$strict)"
