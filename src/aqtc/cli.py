from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from .config import AQTCConfig
from .integrations.nvidia import make_nemotron_adapter
from .operations.business_cycle import AutonomousQuantCompanyAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aqtc", description="Autonomous Quant Company demo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run deterministic business cycle")
    demo.add_argument("--json", action="store_true", help="emit JSON only")
    demo.add_argument(
        "--stripe-mode", choices=["mock", "stripe_test", "test", "stripe"], default=None
    )
    demo.add_argument(
        "--nvidia-mode",
        choices=["mock", "auto", "openrouter", "nvidia", "opencode_zen"],
        default=None,
    )
    demo.add_argument("--policy", type=Path, default=None)
    demo.add_argument(
        "--approve-spend",
        action="store_true",
        help="auto-approve spend above the human approval threshold",
    )

    sub.add_parser("status", help="print current local state")

    report = sub.add_parser("report", help="copy customer report to a path")
    report.add_argument("--out", required=True)
    report.add_argument(
        "--run",
        action="store_true",
        help="run a fresh business cycle before copying the report",
    )
    report.add_argument(
        "--stripe-mode", choices=["mock", "stripe_test", "test", "stripe"], default=None
    )
    report.add_argument(
        "--nvidia-mode",
        choices=["mock", "auto", "openrouter", "nvidia", "opencode_zen"],
        default=None,
    )
    report.add_argument("--policy", type=Path, default=None)
    report.add_argument("--approve-spend", action="store_true")

    regime = sub.add_parser("regime", help="run only the Nemotron/NVIDIA regime summarizer")
    regime.add_argument(
        "--provider",
        choices=["mock", "auto", "openrouter", "nvidia", "opencode_zen"],
        default="auto",
    )
    regime.add_argument("--json", action="store_true")
    return parser


def _config_from_args(args: argparse.Namespace) -> AQTCConfig:
    cfg = AQTCConfig()
    updates: dict[str, object] = {}
    if getattr(args, "stripe_mode", None):
        updates["stripe_mode"] = args.stripe_mode
    if getattr(args, "nvidia_mode", None):
        updates["nvidia_mode"] = args.nvidia_mode
    if getattr(args, "policy", None):
        updates["approval_policy_path"] = args.policy
    if getattr(args, "approve_spend", False):
        updates["auto_approve_spend"] = True
    return replace(cfg, **updates) if updates else cfg


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "regime":
        cfg = replace(AQTCConfig(), nvidia_mode=args.provider)
        adapter = make_nemotron_adapter(
            mode=cfg.nvidia_mode,
            openrouter_model=cfg.openrouter_model,
            nvidia_model=cfg.nvidia_model,
            opencode_zen_model=cfg.opencode_zen_model,
            opencode_zen_base_url=cfg.opencode_zen_base_url,
        )
        summary = adapter.summarize_market_regime({"task": "live smoke test", "paper_mode": True})
        data = {
            "provider": summary.provider,
            "model": summary.model,
            "live": summary.live,
            "text": summary.text,
        }
        if args.json:
            print(json.dumps(data, indent=2, sort_keys=True))
        else:
            print(f"provider: {summary.provider}")
            print(f"model: {summary.model}")
            print(f"live: {summary.live}")
            print(summary.text)
        return 0

    agent = AutonomousQuantCompanyAgent(_config_from_args(args))

    if args.command == "demo":
        result = agent.run_daily_cycle()
        if args.json:
            print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
        else:
            print("AQTC Daily Cycle Complete")
            print(f"Strategy accepted: {result.accepted_strategy}")
            print(f"Rejected unsafe ensemble: {result.rejected_bad_strategy}")
            print(f"Approval: {result.approval_status}")
            print(f"Paper positions: {result.portfolio_positions}")
            print(f"Gross exposure: {result.gross_exposure:.3f}")
            print(f"Stripe mode: {result.stripe_mode}")
            print(f"Nemotron provider: {result.nemotron_provider} live={result.nemotron_live}")
            print(f"Net operating result: ${result.stripe_net_usd:.2f}")
            print(f"Report: {result.report_path}")
        return 0

    if args.command == "status":
        print(json.dumps(agent.status(), indent=2, sort_keys=True))
        return 0

    if args.command == "report":
        if args.run:
            agent.run_daily_cycle()
        src = agent.read_report()
        dst = Path(args.out)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(str(dst))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
