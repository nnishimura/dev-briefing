from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import AuthenticationError, BadRequestError, OpenAI, RateLimitError


@dataclass
class Candidate:
    title: str
    url: str
    source: str
    snippet: str | None = None
    published_at: str | None = None


def search_candidates(topics: list[str]) -> list[Candidate]:
    if not topics:
        logging.warning("No topics configured.")
        return []

    load_dotenv()
    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip().lower()

    prompt = (
        "You are a researcher. Search the web for recent items (prefer last 24 hours) "
        "matching the topics below. Include YouTube videos and tech blog articles. "
        "If exact publish time is not available, still include likely-recent items "
        "and leave published_at null. Always include recent items from "
        "https://www.youtube.com/@CoreDumpped if any. "
        "Return ONLY JSON with this shape: {\"items\": [ ... ]}. Each item object must include: "
        "title, url, source (youtube|blog), snippet, published_at (ISO date if known)."
        "\n\nTopics:\n- " + "\n- ".join(topics)
    )

    try:
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            tool_choice="required",
            input=[
                {"role": "system", "content": "Return strict JSON. No prose."},
                {"role": "user", "content": prompt},
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

    logging.debug("Web search raw output length: %d", len(response.output_text or ""))
    if response.output_text:
        logging.debug("Web search raw output: %s", response.output_text)
    items = _parse_items(response.output_text)
    if not items:
        items = _extract_items_from_tool(response)
    logging.info("Web search returned %d raw items.", len(items))
    candidates: list[Candidate] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        if not title or not url:
            continue
        candidates.append(
            Candidate(
                title=title,
                url=url,
                source=str(item.get("source", "unknown")),
                snippet=item.get("snippet"),
                published_at=item.get("published_at"),
            )
        )
    return candidates


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


def _extract_items_from_tool(response: object) -> list:
    try:
        data = response.model_dump()
    except AttributeError:
        return []
    output = data.get("output", [])
    logging.debug(
        "Output item types: %s",
        [entry.get("type") for entry in output if isinstance(entry, dict)],
    )
    items: list[dict] = []
    annotation_count = 0
    for entry in output:
        if not isinstance(entry, dict):
            continue
        entry_type = entry.get("type")
        if entry_type == "message":
            for part in entry.get("content", []) or []:
                if not isinstance(part, dict):
                    continue
                if part.get("type") != "output_text":
                    continue
                text = part.get("text", "") or ""
                annotations = part.get("annotations", []) or []
                for ann in annotations:
                    if not isinstance(ann, dict):
                        continue
                    if ann.get("type") != "url_citation":
                        continue
                    annotation_count += 1
                    url = ann.get("url")
                    title = ann.get("title") or ""
                    if not url:
                        continue
                    snippet = _snippet_from_text(text, ann.get("start_index"), ann.get("end_index"))
                    items.append(
                        {
                            "title": title.strip() or url,
                            "url": url,
                            "snippet": snippet,
                            "source": "youtube" if "youtube.com" in url else "blog",
                        }
            )
    logging.debug("Found %d url_citation annotations.", annotation_count)
    return items


def _snippet_from_text(text: str, start: int | None, end: int | None) -> str | None:
    if start is None or end is None:
        return None
    try:
        start_i = max(int(start) - 80, 0)
        end_i = min(int(end) + 80, len(text))
        return text[start_i:end_i].strip()
    except (ValueError, TypeError):
        return None
