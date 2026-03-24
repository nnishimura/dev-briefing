from __future__ import annotations

import argparse

from habbit.scheduler import run_daily


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily curated content notifier.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery/curation without sending notifications.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_daily(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
