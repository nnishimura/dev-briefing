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
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the daily send guard.",
    )
    parser.add_argument(
        "--topics",
        help="Path to topics file (default: topics.txt).",
    )
    parser.add_argument(
        "--state",
        help="Path to state file (default: state.json).",
    )
    parser.add_argument(
        "--search-prompt",
        help="Override the search prompt (alternative to SEARCH_PROMPT env var).",
    )
    parser.add_argument(
        "--curate-prompt",
        help="Override the curate prompt (alternative to CURATE_PROMPT env var).",
    )
    return parser


def main() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="%(levelname)s %(message)s")
    args = build_parser().parse_args()
    if args.search_prompt:
        os.environ["SEARCH_PROMPT"] = args.search_prompt
    if args.curate_prompt:
        os.environ["CURATE_PROMPT"] = args.curate_prompt
    topics_path = args.topics or os.getenv("TOPICS_PATH")
    state_path = args.state or os.getenv("STATE_PATH")
    if args.pushbullet_test:
        state = load_state(state_path)
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
    run_daily(
        dry_run=args.dry_run,
        topics_path=topics_path,
        state_path=state_path,
        force=args.force,
    )


if __name__ == "__main__":
    main()
