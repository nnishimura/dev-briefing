from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SentItem:
    title: str
    url: str
    source: str
    date_found: str
    date_sent: str


@dataclass
class State:
    timezone: str = "America/Los_Angeles"
    last_sent_date: str | None = None
    sent: list[SentItem] = field(default_factory=list)

    def record_sent(self, items: list[dict], *, found_date: str, sent_date: str) -> None:
        for item in items:
            self.sent.append(
                SentItem(
                    title=item["title"],
                    url=item["url"],
                    source=item.get("source", "unknown"),
                    date_found=found_date,
                    date_sent=sent_date,
                )
            )


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def state_path(path_override: str | None = None) -> Path:
    if path_override:
        return Path(path_override)
    return repo_root() / "state.json"


def load_state(path_override: str | None = None) -> State:
    path = state_path(path_override)
    if not path.exists():
        return State()
    data = json.loads(path.read_text())
    state = State(
        timezone=data.get("timezone", "America/Los_Angeles"),
        last_sent_date=data.get("last_sent_date"),
    )
    for item in data.get("sent", []):
        state.sent.append(
            SentItem(
                title=item["title"],
                url=item["url"],
                source=item.get("source", "unknown"),
                date_found=item["date_found"],
                date_sent=item["date_sent"],
            )
        )
    return state


def save_state(state: State, path_override: str | None = None) -> None:
    data = {
        "timezone": state.timezone,
        "last_sent_date": state.last_sent_date,
        "sent": [
            {
                "title": item.title,
                "url": item.url,
                "source": item.source,
                "date_found": item.date_found,
                "date_sent": item.date_sent,
            }
            for item in state.sent
        ],
    }
    path = state_path(path_override)
    path.write_text(json.dumps(data, indent=2))
