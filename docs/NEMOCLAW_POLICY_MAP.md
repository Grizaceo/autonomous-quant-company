# NemoClaw policy map (AQTC demo)

AQTC does not embed NemoClaw at runtime. The demo loads `examples/approval_policy.yaml` and enforces it through `LocalPolicyApprovalAdapter` in `src/aqtc/integrations/nemoclaw.py`.

| NemoClaw concept | `approval_policy.yaml` | `nemoclaw.py` behavior |
|------------------|------------------------|-------------------------|
| Deny dangerous actions | `actions.deny` includes `live_broker_execution` | `review_trade` denies when live execution is requested or policy has `live_trading: false` |
| Budget cap | `budget.daily_budget_usd` (25) | Spend events checked against remaining daily budget via Stripe adapter |
| Spend approval threshold | `budget.require_approval_above_usd` (5) + `actions.require_approval: spend_above_threshold` | `review_spend` returns `requires_human_approval` above threshold unless auto-approved |
| Risk limits | `risk.max_gross_exposure`, position caps | Wired into `RiskPolicy` / `RiskGuard` before trade approval |
| Policy identity | `policy_id: aqtc-hackathon-demo-v1` | Returned on every `ApprovalDecision` for audit trails |

**Default demo posture:** paper `MockBroker` only, `live_broker_execution` denied, $2 data spend auto-approved under the $5 threshold.
