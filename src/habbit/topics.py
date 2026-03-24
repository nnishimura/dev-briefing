from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def topics_path() -> Path:
    return repo_root() / ".ai" / "topics.txt"


def load_topics() -> list[str]:
    path = topics_path()
    if not path.exists():
        return []
    topics = []
    for line in path.read_text().splitlines():
        cleaned = line.strip()
        if cleaned:
            topics.append(cleaned)
    return topics
