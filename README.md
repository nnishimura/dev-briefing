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
2. Edit topics in `/Users/naokonishimura/git/habbit/.ai/topics.txt`

## Send Notification Manually
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run habbit
```

Dry run (no Pushbullet send):
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run habbit --dry-run
```

Pushbullet test note:
```bash
uv run habbit --pushbullet-test
```

If you need to re-send on the same day, set `"last_sent_date": null` in
`/Users/naokonishimura/git/habbit/.ai/state.json` and re-run.

## Cron Setup
1. Find `uv` path:
```bash
which uv
```
2. Add a cron entry (example: 8:00am daily). Replace `/ABS/PATH/TO/uv` with the output of `which uv`:
```bash
0 19 * * * cd /Users/naokonishimura/git/habbit && OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO /ABS/PATH/TO/uv run habbit >> /Users/naokonishimura/git/habbit/.ai/cron.log 2>&1
```

## GitHub Actions (Scheduled)
1. Add repo secrets:
   - `OPENAI_API_KEY`
   - `PUSHBULLET_TOKEN`
   - `PUSHBULLET_DEVICE_IDEN` (optional)
2. Workflow file: `/Users/naokonishimura/git/habbit/.github/workflows/daily.yml`
3. Schedule is set to **09:00 America/Los_Angeles** (cron in UTC). Adjust the cron as needed.
4. You can also run it manually from GitHub Actions via **Run workflow**.

## Notes
- The scheduler enforces at-most-once delivery per day using `/Users/naokonishimura/git/habbit/.ai/state.json`.
- Logs are controlled by `LOG_LEVEL` (e.g., `INFO`, `DEBUG`).
