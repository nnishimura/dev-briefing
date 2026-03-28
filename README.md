# dev-briefing

Daily reading contents curated by AI and delivered to your phone via [Pushbullet](https://www.pushbullet.com/), with customizable prompts to tailor what gets curated.

Minimal setup & low operational cost (free aside from OpenAI usage)

## Requirements
- Python 3.14+
- `uv`
- OpenAI API key
- [Pushbullet](https://www.pushbullet.com/) access token & device iden
- Scheduled job runs via GitHub Actions for daily delivery

## Setup
1. Clone this repository
2. Create `.env` from `.env.example` and fill:
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL` (recommended: `gpt-5-mini`)
   - `PUSHBULLET_TOKEN` (See [doc](https://docs.pushbullet.com/#api-quick-start) for details)
   - `PUSHBULLET_DEVICE_IDEN` (optional. Go to pushbullet.com, then the Devices section, you can grab the device_iden for each device by looking at the url.)
3. Edit topics in `topics.txt`

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
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run dev-briefing
```

Dry run (no Pushbullet notification send):
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run dev-briefing --dry-run
```

Force send even if already sent today:
```bash
OPENAI_MODEL=gpt-5-mini LOG_LEVEL=INFO uv run dev-briefing --force
```

## GitHub Actions (Scheduled)
1. Add repo secrets:
   - `OPENAI_API_KEY`
   - `PUSHBULLET_TOKEN`
   - `PUSHBULLET_DEVICE_IDEN` (optional)
2. Workflow file: `.github/workflows/daily.yml`
3. Schedule is set to **09:00 America/Los_Angeles** (cron in UTC). Adjust the cron as needed.
4. You can also run it manually from GitHub Actions via **Run workflow**.
