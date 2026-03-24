# Technical Implementation

This document describes the technical design for the daily curated content notifier.
It incorporates relevant product decisions from `.ai/PRODUCT.md`.

## Stack
- Language: Python 3.12+
- Packaging/runner: `uv`
- LLM + web search: OpenAI Responses API with web search tools
- Notification: Pushbullet (single daily note)

## Key Product Decisions (Copied)
- Discovery and curation use OpenAI GPT models + web search tools (no Ollama dependency for web search).
- Freshness window is 24 hours.
- Target list size is 5 items.
- Must include content from `https://www.youtube.com/@CoreDumpped`.
- Email items include `title`, `URL`, and a short reason.
- Optional phone notification method: Pushbullet (single note per day).

## Repository Layout (Proposed)
- `src/habbit/`
  - `main.py` entrypoint (CLI)
  - `scheduler.py` cron-friendly runner
  - `topics.py` load/validate topics file
  - `search.py` OpenAI web search orchestration
  - `curate.py` ranking + filtering logic
  - `store.py` URL cache + metadata
  - `pushbullet.py` push notifications
- `.ai/topics.txt` user-editable topics list
- `.ai/state.json` cache of sent URLs and metadata
- `.env` secrets (not committed)

## Configuration
Environment variables:
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (default: a GPT model that supports web search tools)
- `TIMEZONE` (default: `America/Los_Angeles`)
- `PUSHBULLET_TOKEN` (optional)
- `PUSHBULLET_DEVICE_IDEN` (optional)

Files:
- `.ai/topics.txt` (one topic per line)
- `.ai/state.json` (cache of sent URLs + metadata)

## Scheduling
- Run once per day with cron or a systemd timer.
- Enforce at-most-once delivery with `.ai/state.json`:
  - If a run already sent today (local time), skip.

## Data Model
State object (JSON):
```json
{
  "last_sent_date": "2026-03-24",
  "sent": [
    {
      "title": "Example title",
      "url": "https://example.com",
      "source": "youtube|blog",
      "date_found": "2026-03-24",
      "date_sent": "2026-03-24"
    }
  ]
}
```

## Discovery + Curation Flow
1. Load topics from `.ai/topics.txt`.
2. For each topic, issue OpenAI web search requests for:
   - YouTube
   - Tech blogs
3. Normalize results: extract `title`, `url`, `snippet`, `published_at` (if available).
4. Filter:
   - Keep items within the last 24 hours if publish time is known.
   - Drop URLs already in `.ai/state.json`.
5. Force-include:
   - Recent items from `https://www.youtube.com/@CoreDumpped`.
6. Ask the model to curate:
   - Score relevance to topics.
   - Select 5 total items.
   - Provide a short 1–2 sentence reason per item.
7. Final validation:
   - Ensure each item has `title`, `url`, `reason`.
   - Deduplicate by URL and title.
8. Send Pushbullet note (single daily notification).
9. Persist updated `.ai/state.json`.

## OpenAI Web Search Integration
- Use the Responses API with web search tools enabled.
- The model is responsible for:
  - Finding candidate URLs.
  - Extracting title/summary signals.
  - Producing final curated list with reasons.

## Pushbullet
- API endpoint: `POST https://api.pushbullet.com/v2/pushes`
- Auth: `Authorization: Bearer <PUSHBULLET_TOKEN>`
- Single daily note:
  - `type`: `note`
  - `title`: `Daily Curated List`
  - `body`: newline-separated list of 5 items (title + URL + reason)
- Optional targeting: include `device_iden`

## Error Handling
- If search returns < 5 items, send fewer items and log a warning.
- If Pushbullet fails, do not update `last_sent_date`.
- If OpenAI call fails, retry with exponential backoff (max 3).

## Testing Strategy
- Unit tests for:
  - Topics parsing
  - Deduplication logic
  - State read/write
  - Pushbullet payload rendering
- Integration test:
  - Mock OpenAI responses
  - Mock Pushbullet API

## Open Questions
- Decide whether Pushbullet notifications are enabled by default.
