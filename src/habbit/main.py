from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from habbit.pushbullet import send_daily_note
from habbit.scheduler import run_daily
from habbit.store import load_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Daily curated content notifier.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run discovery/curation without sending notifications.",
    )
    parser.add_argument(
        "--pushbullet-test",
        action="store_true",
        help="Send a test Pushbullet note and exit.",
    )
    return parser


def main() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    if args.pushbullet_test:
        state = load_state()
        now = datetime.now(ZoneInfo(state.timezone))
        send_daily_note(
            [
                {
                    "title": "Pushbullet test",
                    "url": "https://example.com",
                    "reason": "Test notification from habbit.",
                    "source": "test",
                }
            ],
            now=now,
        )
        return
    run_daily(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
