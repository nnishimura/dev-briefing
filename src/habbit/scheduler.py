from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from habbit.curate import curate_items
from habbit.search import search_candidates
from habbit.store import load_state, save_state
from habbit.topics import load_topics
from habbit.pushbullet import send_daily_note


def run_daily(*, dry_run: bool = False) -> None:
    state = load_state()
    now = datetime.now(ZoneInfo(state.timezone))
    today = now.date().isoformat()

    if state.last_sent_date == today:
        logging.info("Already sent for %s. Skipping.", today)
        return

    topics = load_topics()
    logging.info("Loaded %d topics.", len(topics))
    candidates = search_candidates(topics)
    logging.info("Found %d candidate items.", len(candidates))
    curated = curate_items(candidates, target_count=5)
    logging.info("Curated %d items.", len(curated))

    if not curated:
        logging.warning("No curated items available. Skipping send.")
        return

    if not dry_run:
        send_daily_note(curated, now=now)
        state.last_sent_date = today
        state.record_sent(curated, found_date=today, sent_date=today)
        save_state(state)
