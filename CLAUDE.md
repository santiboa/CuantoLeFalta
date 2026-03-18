# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Cuánto Le Falta is a Twitter/X bot that posts the remaining time until the end of the Mexican presidential term (October 1, 2030). It also runs a Flask landing page with a live countdown. The bot's identity is minimalism and consistency — it is "just a clock."

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium  # only needed for president reply feature

# Run bot locally (DRY_RUN=True by default, logs instead of tweeting)
python3 deployedbot.py

# Run web app
python3 webapp.py

# Run all tests
pytest -v

# Run a single test file or test
pytest test_milestones.py -v
pytest test_countdown.py::TestRemainingTime -v
pytest -k "test_crossed_threshold" -v
```

## Architecture

**Core loop (`deployedbot.py`):** Infinite loop checking every 60 seconds. Three responsibilities:
1. **Periodic tweets** — posts countdown at randomized 8-24 hour intervals
2. **Milestone tweets** — immediate tweet when a countdown threshold is crossed (e.g., 1000 days left, 50% elapsed)
3. **President reply** — daily at ~7:45 AM CDMX, replies to the president's latest tweet with the countdown

**Shared countdown logic (`countdown.py`):** Pure calculation module. Computes remaining time from now until Oct 1, 2030 in Mexico City timezone. Used by bot, milestones, and webapp.

**Milestone system (`milestones.py`):** `MilestoneChecker` class detects when the countdown crosses predefined thresholds (days remaining, percentage elapsed, seconds remaining, days elapsed). Persists tweeted milestones to `milestones_tweeted.json` to avoid duplicates. Has a 5-minute cooldown between milestone tweets.

**President reply (`president_reply.py`):** Uses Playwright with stealth plugin to scrape the president's latest tweet ID (since API read endpoints are paywalled), then replies via Tweepy's free `create_tweet`. Includes anti-detection measures (random delays, realistic viewport, natural navigation flow). Caches last replied ID in `last_replied_id.json`.

**Web app (`webapp.py` + `templates/index.html`):** Flask app serving a landing page with client-side live countdown timer. Reads `latest_tweet.json` (written by the bot after each tweet) to display the most recent post.

## Key Details

- **Timezone:** All time logic uses `America/Mexico_City` via pytz
- **Twitter API:** Tweepy v2 client, free tier (write-only). Credentials via env vars: `CONSUMER_KEY`, `CONSUMER_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`
- **DRY_RUN flag** in `deployedbot.py` controls whether tweets are actually posted (True = log only)
- **State files** (gitignored): `latest_tweet.json`, `last_replied_id.json`, `milestones_tweeted.json`
- **Deprecated files:** `bot.py` and `oneTweet.py` are legacy — `deployedbot.py` is the active production file
- **Deployment:** PythonAnywhere with `deployedbot.py` as always-running task
- **Tweet format:** Spanish language, consistent structure — the bot never editorializes, provocation comes from the countdown itself
