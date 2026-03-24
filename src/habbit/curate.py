from __future__ import annotations

from habbit.search import Candidate


def curate_items(candidates: list[Candidate], *, target_count: int) -> list[dict]:
    # TODO: call OpenAI to rank + summarize and output title/url/reason.
    _ = candidates
    return []
