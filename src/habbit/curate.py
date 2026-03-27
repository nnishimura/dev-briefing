from __future__ import annotations

import json
import logging
import os
import re

from dotenv import load_dotenv
from openai import AuthenticationError, BadRequestError, OpenAI, RateLimitError

from habbit.search import Candidate


def curate_items(candidates: list[Candidate], *, target_count: int) -> list[dict]:
    if not candidates:
        logging.warning("No candidates to curate.")
        return []

    load_dotenv()
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip().lower()

    items = [
        {
            "title": c.title,
            "url": c.url,
            "source": c.source,
            "snippet": c.snippet,
            "published_at": c.published_at,
        }
        for c in candidates
    ]

    prompt = (
        "You are curating a daily list of technical learning content. "
        f"Select exactly {target_count} items. "
        "Return ONLY JSON with this shape: {\"items\": [ ... ]}. "
        "Each item must include: title, url, reason, source. "
        "Reasons should be 1-2 sentences. "
        "If fewer than the target are good, return fewer."
    )

    try:
        response = client.responses.create(
            model=model,
            text={"format": {"type": "json_object"}},
            input=[
                {"role": "system", "content": "Return strict JSON. No prose."},
                {"role": "user", "content": prompt},
                {"role": "user", "content": json.dumps(items)},
            ],
        )
    except AuthenticationError as exc:
        raise RuntimeError("OpenAI authentication failed. Check OPENAI_API_KEY.") from exc
    except RateLimitError as exc:
        raise RuntimeError(
            "OpenAI quota exceeded. Check billing/limits for this API key."
        ) from exc
    except BadRequestError as exc:
        raise RuntimeError(
            f"OpenAI request failed. Check OPENAI_MODEL='{model}' and API key."
        ) from exc

    logging.debug("Curate raw output length: %d", len(response.output_text or ""))
    curated = _parse_items(response.output_text)
    logging.info("Model returned %d curated items.", len(curated))
    cleaned: list[dict] = []
    for item in curated:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        reason = str(item.get("reason", "")).strip()
        if not title or not url or not reason:
            continue
        cleaned.append(
            {
                "title": title,
                "url": url,
                "reason": reason,
                "source": item.get("source", "unknown"),
            }
        )
    return cleaned[:target_count]


def _parse_items(text: str) -> list:
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            items = data.get("items", [])
            return items if isinstance(items, list) else []
        return []
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            return []
        try:
            data = json.loads(match.group(0))
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []
