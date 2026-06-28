from __future__ import annotations

from dataclasses import dataclass

from aqtc.financial_core.risk import RiskAssessment


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    status: str
    reason: str


class LocalPolicyApprovalAdapter:
    """NemoClaw-style local approval layer for safe demo operation."""

    def review_trade(self, assessment: RiskAssessment) -> ApprovalDecision:
        if assessment.allowed:
            return ApprovalDecision(True, "approved", "paper rebalance within local risk policy")
        return ApprovalDecision(False, "blocked", "; ".join(assessment.reasons))
