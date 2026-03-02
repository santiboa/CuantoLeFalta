"""
Reply to the president's latest tweet at 7:45 AM CDMX with the countdown.
Uses Playwright to fetch the latest tweet ID (API read endpoints are paywalled).
Posts the reply via Tweepy (posting is still free tier).
"""
import datetime
import json
import os
import random
import re
import time
from pathlib import Path
from typing import Optional

import tweepy

from countdown import remaining_time, timezone

# --- Config ---
PRESIDENT_X_HANDLE = "Claudiashein"
PROFILE_URL = f"https://x.com/{PRESIDENT_X_HANDLE}"
CACHE_FILE = Path(__file__).parent / "last_replied_id.json"
DRY_RUN = True

# Retry settings
MAX_RETRIES = 4
BASE_DELAY_SECONDS = 6.0

# Startup jitter: wait 27–373 seconds before running (skipped in DRY_RUN)
STARTUP_DELAY_MIN = 27
STARTUP_DELAY_MAX = 373

# Credentials (match deployedbot - consider moving to env vars)
CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY", "fNP3wN6zG2W4PiGETsaFU7Bwi")
CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET", "Tz1HjLXiXdb5Gn9uP2IXocrbLut4fHCOF5EhR1vUOvnHOzvP8F")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "1338193765656264704-FmIfbY97zBxyY0qaNxecI9MmCJUsUv")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "4UK79svSne8789YiXwwrXGnX2FaC2OeuEeZvIJxyrT3RY")

# Realistic user agent (Chrome on Windows, updated periodically)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)


def _human_delay(min_sec: float = 2.0, max_sec: float = 5.0) -> None:
    """Random delay to mimic human behavior."""
    time.sleep(random.uniform(min_sec, max_sec))


def _retry_with_backoff(func, *args, **kwargs):
    """Retry a function with exponential backoff."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_DELAY_SECONDS * (2**attempt) + random.uniform(0, 2)
            print(f"[RETRY] Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}. Waiting {delay:.1f}s...")
            time.sleep(delay)
    raise last_exc


def load_last_replied_id() -> Optional[str]:
    """Load the last tweet ID we replied to from cache."""
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_tweet_id")
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"[WARN] Could not load cache: {e}")
        return None


def save_last_replied_id(tweet_id: str) -> None:
    """Save the tweet ID we replied to."""
    now = datetime.datetime.now(timezone)
    data = {
        "last_tweet_id": tweet_id,
        "replied_at": now.isoformat(),
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_latest_tweet_id() -> Optional[str]:
    """
    Use Playwright to load the president's profile and extract the latest tweet ID.
    Uses natural flow (land on x.com first) and anti-detection measures.
    """
    from playwright.sync_api import sync_playwright
    from playwright_stealth import Stealth

    def _scrape():
        stealth = Stealth(navigator_languages_override=("es-MX", "es"))
        with stealth.use_sync(sync_playwright()) as p:
            # PythonAnywhere: set PLAYWRIGHT_CHROMIUM_PATH=/usr/bin/chromium
            executable = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH")
            launch_kw: dict = {
                "headless": True,
                "args": ["--disable-gpu", "--no-sandbox", "--headless"],
            }
            if executable:
                launch_kw["executable_path"] = executable

            browser = p.chromium.launch(**launch_kw)

            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1366, "height": 768},
                locale="es-MX",
            )

            page = context.new_page()
            # Stealth is applied automatically to pages via use_sync

            # Natural flow: land on x.com first, then navigate to profile
            page.goto("https://x.com", wait_until="domcontentloaded", timeout=30000)
            _human_delay(2.5, 5.0)

            page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=30000)
            _human_delay(2.0, 4.0)

            # Light scroll to trigger lazy load and mimic human
            page.evaluate("window.scrollBy(0, 200)")
            _human_delay(1.0, 2.5)

            # Extract tweet ID from links matching /handle/status/ID (stable URL pattern)
            pattern = re.compile(rf"/{PRESIDENT_X_HANDLE}/status/(\d+)")
            links = page.locator('a[href*="/status/"]').all()
            for link in links:
                href = link.get_attribute("href") or ""
                m = pattern.search(href)
                if m:
                    browser.close()
                    return m.group(1)

            browser.close()
            return None

    return _retry_with_backoff(_scrape)


def main() -> None:
    """Main entry: get latest tweet, reply if new, cache ID."""
    now = datetime.datetime.now(timezone)
    print(f"[{now.isoformat()}] President reply job started (DRY_RUN={DRY_RUN})")

    if not DRY_RUN:
        delay = random.uniform(STARTUP_DELAY_MIN, STARTUP_DELAY_MAX)
        print(f"[JITTER] Waiting {delay:.1f}s before running...")
        time.sleep(delay)

    latest_id = get_latest_tweet_id()
    if not latest_id:
        print("[SKIP] Could not fetch latest tweet ID")
        return

    print(f"[OK] Latest tweet ID: {latest_id}")

    cached_id = load_last_replied_id()
    if cached_id == latest_id:
        print(f"[SKIP] Already replied to {latest_id}")
        return

    tweet_text = remaining_time()
    if tweet_text == "Ya acabó.":
        print("[SKIP] Countdown ended, not replying")
        return

    if DRY_RUN:
        print(f"[DRY RUN] Would reply to {latest_id}: {tweet_text[:80]}...")
        return

    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    try:
        client.create_tweet(text=tweet_text, in_reply_to_tweet_id=latest_id)
        save_last_replied_id(latest_id)
        print(f"[SUCCESS] Replied to {latest_id}")
    except tweepy.TweepyException as e:
        print(f"[ERROR] Failed to reply: {e}")
        raise


if __name__ == "__main__":
    main()
