from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from habbit.curate import curate_items
from habbit.search import search_candidates
from habbit.store import load_state, save_state
from habbit.topics import load_topics
from habbit.pushbullet import send_daily_note


def run_daily(
    *,
    dry_run: bool = False,
    topics_path: str | None = None,
    state_path: str | None = None,
    force: bool = False,
) -> None:
    state = load_state(state_path)
    now = datetime.now(ZoneInfo(state.timezone))
    today = now.date().isoformat()

    if state.last_sent_date == today and not force:
        logging.info("Already sent for %s. Skipping.", today)
        return

    topics = load_topics(topics_path)
    logging.info("Loaded %d topics.", len(topics))
    if not topics:
        logging.warning("No topics configured. Add topics to topics.txt and retry.")
        return
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
        save_state(state, state_path)
