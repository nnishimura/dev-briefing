# habbit

Daily curated learning notifications (YouTube + tech blogs) delivered via Pushbullet.

## Requirements
- Python 3.14+
- `uv`
- OpenAI API key
- Pushbullet access token (and optional device iden)

## Setup
1. Create `.env` from `.env.example` and fill:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (recommended: `gpt-5-mini`)
   - `PUSHBULLET_TOKEN`
   - `PUSHBULLET_DEVICE_IDEN` (optional)
2. Edit topics in `topics.txt`

## Configuration
Environment variables (all optional unless noted):
- Required: `OPENAI_API_KEY`, `PUSHBULLET_TOKEN`
- Optional: `OPENAI_MODEL`, `TIMEZONE`, `LOG_LEVEL`
- Optional paths: `TOPICS_PATH`, `STATE_PATH`

CLI overrides:
- `--topics` path to topics file
- `--state` path to state file
- `--search-prompt` override search prompt text
- `--curate-prompt` override curate prompt text

Prompt env overrides:
- `SEARCH_PROMPT` (supports `{topics}` placeholder)
- `CURATE_PROMPT` (supports `{target_count}` placeholder)

## Send Notification Manually
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run habbit
```

Dry run (no Pushbullet send):
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run habbit --dry-run
```

Force send even if already sent today:
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run habbit --force
```

Pushbullet test note:
```bash
uv run habbit --pushbullet-test
```

If you need to re-send on the same day, set `"last_sent_date": null` in
`state.json` and re-run.

## Cron Setup
1. Find `uv` path:
```bash
which uv
```
2. Add a cron entry (example: 8:00am daily). Replace `/ABS/PATH/TO/uv` with the output of `which uv`:
```bash
0 19 * * * cd /PATH/TO/habbit && OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO /ABS/PATH/TO/uv run habbit >> cron.log 2>&1
```

## GitHub Actions (Scheduled)
1. Add repo secrets:
   - `OPENAI_API_KEY`
   - `PUSHBULLET_TOKEN`
   - `PUSHBULLET_DEVICE_IDEN` (optional)
2. Workflow file: `.github/workflows/daily.yml`
3. Schedule is set to **09:00 America/Los_Angeles** (cron in UTC). Adjust the cron as needed.
4. You can also run it manually from GitHub Actions via **Run workflow**.

## Notes
- The scheduler enforces at-most-once delivery per day using `state.json`.
- Logs are controlled by `LOG_LEVEL` (e.g., `INFO`, `DEBUG`).
