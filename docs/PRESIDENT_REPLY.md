# President Reply Feature

Replies to the president's latest tweet with the countdown at **7:45 AM CDMX** (before the morning briefing).

## Why Playwright?

Twitter/X's API paywall blocks **read** endpoints (timeline, user tweets, mentions). **Posting** (including replies) still works on the free tier. So we:

1. **Scrape** the president's profile with Playwright to get the latest tweet ID
2. **Reply** via Tweepy's `create_tweet(in_reply_to_tweet_id=...)`

## Setup

### Local

```bash
pip install -r requirements.txt
playwright install chromium
```

### PythonAnywhere (paid account)

Playwright works on PythonAnywhere with system Chromium. See [their docs](https://help.pythonanywhere.com/pages/Playwright/).

1. Create a virtualenv and install deps:
   ```bash
   mkvirtualenv cuantolefalta --python=python3.10
   pip install -r requirements.txt
   # Do NOT run playwright install - use system Chromium
   ```

2. Set env var for Chromium path:
   ```
   PLAYWRIGHT_CHROMIUM_PATH=/usr/bin/chromium
   ```

3. Schedule a task at **7:45 AM** (America/Mexico_City):
   ```
   /home/yourusername/.virtualenvs/cuantolefalta/bin/python /home/yourusername/CuantoLeFalta/president_reply.py
   ```

4. (Optional) Add schedule jitter: run at 7:43–7:47 instead of exactly 7:45 to avoid robotic patterns.

## Config

| Variable | Purpose |
|----------|---------|
| `DRY_RUN` | Set to `False` to actually post replies |
| `PRESIDENT_X_HANDLE` | Handle to monitor (`Claudiashein`) |
| `PLAYWRIGHT_CHROMIUM_PATH` | Set to `/usr/bin/chromium` on PythonAnywhere |

## Anti-Detection Measures

- **playwright-stealth**: Masks `navigator.webdriver` and automation signals
- **Natural flow**: Land on x.com first, then navigate to profile (not direct)
- **Random delays**: 2–6s between actions
- **Realistic viewport**: 1366×768, Chrome user-agent, `es-MX` locale
- **Retry with exponential backoff**: Max 4 retries, cap delay
- **Tweet ID from URL**: Extract from `a[href*="/status/"]` (stable pattern)

## Cache

`last_replied_id.json` stores the last tweet ID we replied to. Prevents double replies. Not committed to git.
