from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from aqtc.financial_core.risk import RiskAssessment


@dataclass(frozen=True)
class ApprovalPolicy:
    policy_id: str = "aqtc-demo-policy-v1"
    max_gross_exposure: float = 4.0
    max_active_positions: int = 8
    max_single_position_weight: float = 2.0
    live_trading: bool = False
    daily_budget_usd: float = 25.0
    require_approval_above_usd: float = 5.0
    deny_actions: list[str] = field(default_factory=lambda: ["live_broker_execution"])
    require_approval_actions: list[str] = field(default_factory=lambda: ["spend_above_threshold"])


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    status: str
    reason: str
    policy_id: str = "aqtc-demo-policy-v1"
    checks: dict[str, Any] = field(default_factory=dict)


def load_approval_policy(path: Path | str | None) -> ApprovalPolicy:
    if not path:
        return ApprovalPolicy()
    p = Path(path)
    if not p.exists():
        return ApprovalPolicy()
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    risk = raw.get("risk", {})
    budget = raw.get("budget", {})
    actions = raw.get("actions", {})
    return ApprovalPolicy(
        policy_id=str(raw.get("policy_id", "aqtc-demo-policy-v1")),
        max_gross_exposure=float(risk.get("max_gross_exposure", 4.0)),
        max_active_positions=int(risk.get("max_active_positions", 8)),
        max_single_position_weight=float(risk.get("max_single_position_weight", 2.0)),
        live_trading=bool(risk.get("live_trading", False)),
        daily_budget_usd=float(budget.get("daily_budget_usd", 25.0)),
        require_approval_above_usd=float(budget.get("require_approval_above_usd", 5.0)),
        deny_actions=list(actions.get("deny", ["live_broker_execution"])),
        require_approval_actions=list(actions.get("require_approval", ["spend_above_threshold"])),
    )


class LocalPolicyApprovalAdapter:
    """NemoClaw-style local approval layer for safe demo operation."""

    def __init__(self, policy: ApprovalPolicy | None = None):
        self.policy = policy or ApprovalPolicy()

    def review_trade(self, assessment: RiskAssessment) -> ApprovalDecision:
        checks = {
            "gross_exposure": assessment.gross_exposure,
            "active_positions": assessment.active_positions,
            "risk_allowed": assessment.allowed,
        }
        if assessment.allowed:
            return ApprovalDecision(
                True,
                "approved",
                "paper rebalance within local risk policy",
                policy_id=self.policy.policy_id,
                checks=checks,
            )
        return ApprovalDecision(
            False,
            "blocked",
            "; ".join(assessment.reasons),
            policy_id=self.policy.policy_id,
            checks=checks | {"reasons": assessment.reasons},
        )

    def review_spend(self, *, amount_usd: float, spent_so_far_usd: float = 0.0) -> ApprovalDecision:
        projected = spent_so_far_usd + amount_usd
        checks = {
            "amount_usd": amount_usd,
            "spent_so_far_usd": spent_so_far_usd,
            "projected_spend_usd": projected,
            "daily_budget_usd": self.policy.daily_budget_usd,
            "require_approval_above_usd": self.policy.require_approval_above_usd,
        }
        if projected > self.policy.daily_budget_usd:
            return ApprovalDecision(
                False,
                "blocked",
                f"budget exceeded: {projected:.2f} > {self.policy.daily_budget_usd:.2f}",
                policy_id=self.policy.policy_id,
                checks=checks,
            )
        if amount_usd > self.policy.require_approval_above_usd:
            return ApprovalDecision(
                False,
                "requires_human_approval",
                f"spend {amount_usd:.2f} exceeds approval threshold",
                policy_id=self.policy.policy_id,
                checks=checks,
            )
        return ApprovalDecision(
            True,
            "approved",
            "spend within autonomous budget policy",
            policy_id=self.policy.policy_id,
            checks=checks,
        )
