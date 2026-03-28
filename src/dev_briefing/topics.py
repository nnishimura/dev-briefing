from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def topics_path(path_override: str | None = None) -> Path:
    if path_override:
        return Path(path_override)
    return repo_root() / "topics.txt"


def load_topics(path_override: str | None = None) -> list[str]:
    path = topics_path(path_override)
    if not path.exists():
        return []
    topics = []
    for line in path.read_text().splitlines():
        cleaned = line.strip()
        if cleaned:
            topics.append(cleaned)
    return topics
