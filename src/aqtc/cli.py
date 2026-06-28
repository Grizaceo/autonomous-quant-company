from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import AQTCConfig
from .operations.business_cycle import AutonomousQuantCompanyAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aqtc", description="Autonomous Quant Company demo CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run deterministic business cycle")
    demo.add_argument("--json", action="store_true", help="emit JSON only")

    sub.add_parser("status", help="print current local state")

    report = sub.add_parser("report", help="write current customer report to a path")
    report.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    agent = AutonomousQuantCompanyAgent(AQTCConfig())

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
            print(f"Net operating result: ${result.stripe_net_usd:.2f}")
            print(f"Report: {result.report_path}")
        return 0

    if args.command == "status":
        print(json.dumps(agent.status(), indent=2, sort_keys=True))
        return 0

    if args.command == "report":
        result = agent.run_daily_cycle()
        src = Path(result.report_path)
        dst = Path(args.out)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        print(str(dst))
        return 0

    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
