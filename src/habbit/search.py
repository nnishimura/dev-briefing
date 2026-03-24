from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Candidate:
    title: str
    url: str
    source: str
    snippet: str | None = None
    published_at: str | None = None


def search_candidates(topics: list[str]) -> list[Candidate]:
    # TODO: integrate OpenAI Responses API web search tool.
    _ = topics
    return []
