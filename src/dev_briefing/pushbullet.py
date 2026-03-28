from __future__ import annotations

import logging
import os
from datetime import datetime

import httpx
from dotenv import load_dotenv


class PushbulletError(RuntimeError):
    pass


def send_daily_note(items: list[dict], *, now: datetime) -> None:
    if not items:
        return

    load_dotenv()
    token = os.getenv("PUSHBULLET_TOKEN")
    if not token:
        raise PushbulletError("Missing PUSHBULLET_TOKEN.")

    device_iden = os.getenv("PUSHBULLET_DEVICE_IDEN")
    title = f"Daily Curated List ({now.date().isoformat()})"
    body = _format_body(items)

    payload: dict[str, str] = {
        "type": "note",
        "title": title,
        "body": body,
    }
    if device_iden:
        payload["device_iden"] = device_iden

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            "https://api.pushbullet.com/v2/pushes",
            json=payload,
            headers=headers,
        )
    if response.status_code >= 400:
        raise PushbulletError(
            f"Pushbullet failed: {response.status_code} {response.text}"
        )
    logging.info("Pushbullet sent: %s", response.status_code)


def _format_body(items: list[dict]) -> str:
    lines: list[str] = []
    for idx, item in enumerate(items, start=1):
        title = str(item.get("title", "")).strip()
        url = str(item.get("url", "")).strip()
        reason = str(item.get("reason", "")).strip()
        lines.append(f"{idx}) {title}")
        lines.append(f"   {url}")
        if reason:
            lines.append(f"   {reason}")
        lines.append("")
    return "\n".join(lines).strip()
