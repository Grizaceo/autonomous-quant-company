from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from aqtc.config import AQTCConfig
from aqtc.events import BusinessEvent, EventLog
from aqtc.financial_core.portfolio import MockBroker
from aqtc.financial_core.provenance import load_alpha_provenance
from aqtc.financial_core.risk import RiskGuard, RiskPolicy
from aqtc.financial_core.signals import cap_signal, load_latest_signal
from aqtc.financial_core.validation import compare_candidate_vs_rejected, load_json, passes_gate4
from aqtc.integrations.nemoclaw import LocalPolicyApprovalAdapter, load_approval_policy
from aqtc.integrations.nvidia import make_nemotron_adapter
from aqtc.integrations.stripe_skills import StripeLedger, make_stripe_adapter


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
    nemotron_provider: str
    nemotron_live: bool
    stripe_mode: str
    spend_status: str = "completed"
    accepted_candidate_sharpe: float | None = None
    rejected_candidate_sharpe: float | None = None
    rejected_candidate_max_drawdown: float | None = None
    rejection_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AutonomousQuantCompanyAgent:
    def __init__(self, config: AQTCConfig | None = None):
        self.config = config or AQTCConfig()
        self.config.ensure_state()
        self.policy = load_approval_policy(self.config.approval_policy_path)
        self.events = EventLog(self.config.state_dir / "events.jsonl")
        self.ledger = StripeLedger(self.config.state_dir / "stripe_ledger.json")
        self.stripe = make_stripe_adapter(
            self.ledger,
            mode=self.config.stripe_mode,
            daily_budget_usd=self.policy.daily_budget_usd,
            currency=self.config.stripe_currency,
        )
        self.nemotron = make_nemotron_adapter(
            mode=self.config.nvidia_mode,
            openrouter_model=self.config.openrouter_model,
            nvidia_model=self.config.nvidia_model,
            opencode_zen_model=self.config.opencode_zen_model,
            opencode_zen_base_url=self.config.opencode_zen_base_url,
        )
        self.approvals = LocalPolicyApprovalAdapter(self.policy)
        self.broker = MockBroker(self.config.state_dir / "portfolio_state.json")

    def _event(self, action: str, summary: str, **kwargs: Any) -> None:
        self.events.append(
            BusinessEvent(actor="aqtc-agent", action=action, summary=summary, **kwargs)
        )

    def reset_demo_state(self) -> None:
        """Reset local demo state so every `aqtc demo` is deterministic."""
        self.events.path.write_text("", encoding="utf-8")
        self.ledger.path.write_text("[]", encoding="utf-8")
        portfolio_path = self.config.state_dir / "portfolio_state.json"
        if portfolio_path.exists():
            portfolio_path.unlink()

    def run_daily_cycle(
        self,
        *,
        reset: bool = True,
        auto_approve_spend: bool | None = None,
    ) -> BusinessCycleResult:
        if reset:
            self.reset_demo_state()
        approve_spend = (
            self.config.auto_approve_spend if auto_approve_spend is None else auto_approve_spend
        )
        data = self.config.demo_data_dir
        provenance = load_alpha_provenance(data)

        production = load_json(data / "walkforward_report.json")
        rejected = load_json(data / "rejected_ensemble_2019.json")
        comparison = compare_candidate_vs_rejected(production, rejected)
        regime = self.nemotron.summarize_market_regime(
            {
                "candidate_sharpe": comparison["candidate_sharpe"],
                "rejected_sharpe": comparison["rejected_sharpe"],
                "max_gross_exposure": self.policy.max_gross_exposure,
                "live_trading": self.policy.live_trading,
            }
        )
        self._event(
            "summarize_regime",
            regime.text,
            evidence={"provider": regime.provider, "model": regime.model, "live": regime.live},
        )

        spend_status = "completed"
        spend_approval = self.approvals.review_spend(
            amount_usd=self.config.data_purchase_usd,
            auto_approve=approve_spend,
        )
        self._event(
            "approve_spend",
            spend_approval.reason,
            approval_status=spend_approval.status,
            evidence=spend_approval.checks,
        )
        if spend_approval.approved:
            spend = self.stripe.spend("premium market data sample", self.config.data_purchase_usd)
            self._event(
                "spend",
                spend.description,
                amount_usd=spend.amount_usd,
                evidence={
                    "mode": spend.mode,
                    "external_id": spend.external_id,
                    "status": spend.status,
                },
            )
        elif spend_approval.status == "requires_human_approval":
            spend_status = "skipped_pending_approval"
            self._event(
                "skip_spend",
                spend_approval.reason,
                approval_status=spend_approval.status,
            )
        else:
            spend_status = "blocked"
            self._event(
                "skip_spend",
                spend_approval.reason,
                approval_status=spend_approval.status,
            )

        decision = passes_gate4(production)
        bad_decision = passes_gate4(rejected)
        rejection_reason = provenance["rejected"]["reason"]
        self._event("validate_strategy", decision.reason, evidence={"comparison": comparison})
        self._event(
            "reject_strategy",
            bad_decision.reason,
            evidence={
                "source": provenance["rejected"]["name"],
                "sharpe": provenance["rejected"]["sharpe"],
                "max_drawdown": provenance["rejected"]["max_drawdown"],
                "reason": rejection_reason,
            },
        )

        raw_signal = load_latest_signal(data / "live_signals.jsonl")
        risk_policy = RiskPolicy(
            max_gross_exposure=self.policy.max_gross_exposure,
            max_active_positions=self.policy.max_active_positions,
            max_single_position_weight=self.policy.max_single_position_weight,
            live_trading=self.policy.live_trading,
        )
        capped_signal = cap_signal(raw_signal, max_gross=risk_policy.max_gross_exposure)
        live_requested = self.config.live_trading
        assessment = RiskGuard(risk_policy).assess(capped_signal, live_requested=live_requested)
        approval = self.approvals.review_trade(assessment, live_requested=live_requested)
        self._event(
            "approve_trade",
            approval.reason,
            approval_status=approval.status,
            evidence=approval.checks,
        )

        if approval.approved and decision.accepted:
            portfolio = self.broker.rebalance(capped_signal)
            self._event(
                "execute_paper_rebalance",
                "MockBroker portfolio updated",
                evidence=portfolio.to_dict(),
            )
        else:
            portfolio = self.broker.load()
            self._event("skip_execution", "trade not executed", approval_status=approval.status)

        earn = self.stripe.earn("customer quant research report", self.config.report_price_usd)
        self._event(
            "earn",
            earn.description,
            amount_usd=earn.amount_usd,
            evidence={"mode": earn.mode, "external_id": earn.external_id, "status": earn.status},
        )

        report_path = self.generate_report(
            decision=decision,
            comparison=comparison,
            approval=approval,
            portfolio=portfolio,
            spend_status=spend_status,
            provenance=provenance,
            bad_decision=bad_decision,
        )
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
            nemotron_provider=regime.provider,
            nemotron_live=regime.live,
            stripe_mode=self.stripe.mode,
            spend_status=spend_status,
            accepted_candidate_sharpe=provenance["accepted"]["mean_sharpe"],
            rejected_candidate_sharpe=provenance["rejected"]["sharpe"],
            rejected_candidate_max_drawdown=provenance["rejected"]["max_drawdown"],
            rejection_reason=rejection_reason,
        )

    def generate_report(
        self,
        *,
        decision: Any,
        comparison: dict[str, float],
        approval: Any,
        portfolio: Any,
        spend_status: str = "completed",
        provenance: dict[str, Any] | None = None,
        bad_decision: Any | None = None,
    ) -> Path:
        provenance = provenance or load_alpha_provenance(self.config.demo_data_dir)
        accepted = provenance["accepted"]
        rejected = provenance["rejected"]
        cfg = provenance["production_config"]
        path = self.config.state_dir / "customer_report.md"
        rejected_section = ""
        if bad_decision is not None:
            rejected_section = f"""
## Rejected candidate

- Name: {rejected["name"]}
- Sharpe: {rejected["sharpe"]:.3f}
- Max drawdown: {rejected["max_drawdown"]:.3f}
- Reason: {rejected["reason"]}
- Gate result: {bad_decision.reason}
"""
        content = f"""# Autonomous Quant Company Report

## Research provenance

- Engine: {provenance["engine"]}
- Model: {provenance["model"]} ({provenance["genotype_dim"]}D genotype)
- Algorithm: {provenance["algorithm"]}
- Mean Sharpe: {accepted["mean_sharpe"]:.3f} ({accepted["n_folds"]} folds, {accepted["positive_fold_ratio"]:.0%} positive)
- Mean max drawdown: {accepted["mean_max_drawdown"]:.3f}
- Config: d_model={cfg["d_model"]}, pop_size={cfg["pop_size"]}, reward_horizon={cfg["reward_horizon"]}
{rejected_section}
## Strategy decision

- Accepted production strategy: {decision.accepted}
- Reason: {decision.reason}
- Sharpe delta vs rejected ensemble: {comparison["sharpe_delta"]:.3f}
- Drawdown improvement vs rejected ensemble: {comparison["drawdown_delta"]:.3f}

## Approval

- Status: {approval.status}
- Reason: {approval.reason}
- Policy: {approval.policy_id}

## Procurement

- Spend status: {spend_status}

## Paper portfolio

- Mode: {portfolio.mode}
- Positions: {len(portfolio.positions)}
- Gross exposure: {sum(abs(v) for v in portfolio.positions.values()):.3f}

## Business ledger

- Stripe mode: {self.stripe.mode}
- Net operating result: ${self.ledger.net():.2f}
"""
        path.write_text(content, encoding="utf-8")
        return path

    def read_report(self) -> Path:
        path = self.config.state_dir / "customer_report.md"
        if not path.exists():
            raise FileNotFoundError(
                f"No report at {path}. Run `aqtc demo` or `aqtc report --run` first."
            )
        return path

    def get_provenance(self) -> dict[str, Any]:
        return load_alpha_provenance(self.config.demo_data_dir)

    def status(self) -> dict[str, Any]:
        report_path = self.config.state_dir / "customer_report.md"
        return {
            "events": self.events.read(),
            "ledger": self.ledger.read(),
            "portfolio": self.broker.load().to_dict(),
            "policy": asdict(self.policy),
            "provenance": self.get_provenance(),
            "config": {
                "stripe_mode": self.config.stripe_mode,
                "nvidia_mode": self.config.nvidia_mode,
                "live_trading": self.config.live_trading,
                "auto_approve_spend": self.config.auto_approve_spend,
            },
            "report_path": str(report_path) if report_path.exists() else None,
        }
