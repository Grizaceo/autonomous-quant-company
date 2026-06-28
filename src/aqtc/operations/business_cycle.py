from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from aqtc.config import AQTCConfig
from aqtc.events import BusinessEvent, EventLog
from aqtc.financial_core.portfolio import MockBroker
from aqtc.financial_core.risk import RiskGuard, RiskPolicy
from aqtc.financial_core.signals import cap_signal, load_latest_signal
from aqtc.financial_core.validation import compare_candidate_vs_rejected, load_json, passes_gate4
from aqtc.integrations.nemoclaw import LocalPolicyApprovalAdapter
from aqtc.integrations.nvidia import MockNemotronAdapter
from aqtc.integrations.stripe_skills import MockStripeAdapter, StripeLedger


@dataclass(frozen=True)
class BusinessCycleResult:
    accepted_strategy: bool
    rejected_bad_strategy: bool
    approval_status: str
    portfolio_positions: int
    gross_exposure: float
    stripe_net_usd: float
    report_path: str
    event_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AutonomousQuantCompanyAgent:
    def __init__(self, config: AQTCConfig | None = None):
        self.config = config or AQTCConfig()
        self.config.ensure_state()
        self.events = EventLog(self.config.state_dir / "events.jsonl")
        self.ledger = StripeLedger(self.config.state_dir / "stripe_ledger.json")
        self.stripe = MockStripeAdapter(
            self.ledger,
            mode=self.config.stripe_mode,
            daily_budget_usd=self.config.daily_budget_usd,
        )
        self.nemotron = MockNemotronAdapter()
        self.approvals = LocalPolicyApprovalAdapter()
        self.broker = MockBroker(self.config.state_dir / "portfolio_state.json")

    def _event(self, action: str, summary: str, **kwargs: Any) -> None:
        self.events.append(BusinessEvent(actor="aqtc-agent", action=action, summary=summary, **kwargs))

    def reset_demo_state(self) -> None:
        """Reset local demo state so every `aqtc demo` is deterministic."""
        self.events.path.write_text("", encoding="utf-8")
        self.ledger.path.write_text("[]", encoding="utf-8")
        portfolio_path = self.config.state_dir / "portfolio_state.json"
        if portfolio_path.exists():
            portfolio_path.unlink()

    def run_daily_cycle(self, *, reset: bool = True) -> BusinessCycleResult:
        if reset:
            self.reset_demo_state()
        data = self.config.demo_data_dir

        regime = self.nemotron.summarize_market_regime()
        self._event("summarize_regime", regime.text, evidence={"provider": regime.provider})

        spend = self.stripe.spend("premium market data sample", 2.00)
        self._event("spend", spend.description, amount_usd=spend.amount_usd, evidence={"mode": spend.mode})

        production = load_json(data / "walkforward_report.json")
        rejected = load_json(data / "rejected_ensemble_2019.json")
        decision = passes_gate4(production)
        bad_decision = passes_gate4(rejected)
        comparison = compare_candidate_vs_rejected(production, rejected)
        self._event("validate_strategy", decision.reason, evidence={"comparison": comparison})
        self._event("reject_strategy", bad_decision.reason, evidence={"source": "2019+ ensemble holdout"})

        raw_signal = load_latest_signal(data / "live_signals.jsonl")
        policy = RiskPolicy(max_gross_exposure=4.0, max_active_positions=8, live_trading=self.config.live_trading)
        capped_signal = cap_signal(raw_signal, max_gross=policy.max_gross_exposure)
        assessment = RiskGuard(policy).assess(capped_signal, live_requested=False)
        approval = self.approvals.review_trade(assessment)
        self._event(
            "approve_trade",
            approval.reason,
            approval_status=approval.status,
            evidence={"gross_exposure": assessment.gross_exposure, "active_positions": assessment.active_positions},
        )

        if approval.approved and decision.accepted:
            portfolio = self.broker.rebalance(capped_signal)
            self._event("execute_paper_rebalance", "MockBroker portfolio updated", evidence=portfolio.to_dict())
        else:
            portfolio = self.broker.load()
            self._event("skip_execution", "trade not executed", approval_status=approval.status)

        earn = self.stripe.earn("customer quant research report", 19.00)
        self._event("earn", earn.description, amount_usd=earn.amount_usd, evidence={"mode": earn.mode})

        report_path = self.generate_report(decision=decision, comparison=comparison, approval=approval, portfolio=portfolio)
        self._event("generate_report", f"report written to {report_path}")

        return BusinessCycleResult(
            accepted_strategy=decision.accepted,
            rejected_bad_strategy=not bad_decision.accepted,
            approval_status=approval.status,
            portfolio_positions=len(portfolio.positions),
            gross_exposure=round(sum(abs(v) for v in portfolio.positions.values()), 6),
            stripe_net_usd=self.ledger.net(),
            report_path=str(report_path),
            event_count=len(self.events.read()),
        )

    def generate_report(self, *, decision: Any, comparison: dict[str, float], approval: Any, portfolio: Any) -> Path:
        path = self.config.state_dir / "customer_report.md"
        content = f"""# Autonomous Quant Company Report

## Strategy decision

- Accepted production strategy: {decision.accepted}
- Reason: {decision.reason}
- Sharpe delta vs rejected ensemble: {comparison['sharpe_delta']:.3f}
- Drawdown improvement vs rejected ensemble: {comparison['drawdown_delta']:.3f}

## Approval

- Status: {approval.status}
- Reason: {approval.reason}

## Paper portfolio

- Mode: {portfolio.mode}
- Positions: {len(portfolio.positions)}
- Gross exposure: {sum(abs(v) for v in portfolio.positions.values()):.3f}

## Business ledger

- Net operating result: ${self.ledger.net():.2f}
"""
        path.write_text(content, encoding="utf-8")
        return path

    def status(self) -> dict[str, Any]:
        return {
            "events": self.events.read(),
            "ledger": self.ledger.read(),
            "portfolio": self.broker.load().to_dict(),
        }
