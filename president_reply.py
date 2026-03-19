"""
Quote-tweet the president's latest tweet with the countdown.
Uses X API v2 (via Tweepy) to read the latest tweet and post a quote tweet.
Polls every 30 minutes; controlled by deployedbot.py's main loop.
"""
import datetime
import json
import os
from pathlib import Path
from typing import Optional

import tweepy
from dotenv import load_dotenv

load_dotenv()

from countdown import remaining_time, timezone

# --- Config ---
PRESIDENT_X_HANDLE = "Claudiashein"
CACHE_FILE = Path(__file__).parent / "last_replied_id.json"
DRY_RUN = True

# Credentials
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")

# Cache the president's numeric user ID to avoid repeated lookups
_president_user_id: Optional[str] = None


def _get_read_client() -> tweepy.Client:
    """Client for reading (uses Bearer Token, app-only auth)."""
    return tweepy.Client(bearer_token=BEARER_TOKEN)


def _get_write_client() -> tweepy.Client:
    """Client for writing (uses OAuth 1.0a user context)."""
    return tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )


REPLIED_IDS_LIMIT = 3


def load_replied_ids() -> list:
    """Load the list of recently replied tweet IDs from cache."""
    if not CACHE_FILE.exists():
        return []
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Support old single-ID format
            if "replied_ids" in data:
                return data["replied_ids"]
            legacy = data.get("last_tweet_id")
            return [legacy] if legacy else []
    except (json.JSONDecodeError, IOError, KeyError) as e:
        print(f"[WARN] Could not load cache: {e}")
        return []


def save_replied_id(tweet_id: str) -> None:
    """Append tweet ID to the replied list, keeping the last REPLIED_IDS_LIMIT entries."""
    replied_ids = load_replied_ids()
    if tweet_id not in replied_ids:
        replied_ids.append(tweet_id)
    replied_ids = replied_ids[-REPLIED_IDS_LIMIT:]
    now = datetime.datetime.now(timezone)
    data = {
        "replied_ids": replied_ids,
        "last_replied_at": now.isoformat(),
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_president_user_id(client: tweepy.Client) -> Optional[str]:
    """Look up the president's numeric user ID by username. Cached after first call."""
    global _president_user_id
    if _president_user_id is not None:
        return _president_user_id

    response = client.get_user(username=PRESIDENT_X_HANDLE)
    if response.data:
        _president_user_id = str(response.data.id)
        print(f"[OK] Resolved @{PRESIDENT_X_HANDLE} -> user ID {_president_user_id}")
        return _president_user_id

    print(f"[ERROR] Could not resolve @{PRESIDENT_X_HANDLE}")
    return None


def get_latest_tweet_id(client: tweepy.Client = None) -> Optional[str]:
    """
    Fetch the president's latest tweet via X API v2.
    Returns the tweet ID, or None if unavailable.
    """
    if client is None:
        client = _get_read_client()

    user_id = get_president_user_id(client)
    if not user_id:
        return None

    response = client.get_users_tweets(
        id=user_id,
        max_results=5,
        exclude=["retweets", "replies"],
        tweet_fields=["created_at"],
    )

    if response.data:
        latest = response.data[0]
        print(f"[OK] Latest tweet ID: {latest.id} (created: {latest.created_at})")
        return str(latest.id)

    print("[WARN] No tweets found for user")
    return None


def main() -> None:
    """Main entry: get latest tweet, quote-tweet if new, cache ID."""
    now = datetime.datetime.now(timezone)
    print(f"[{now.isoformat()}] President reply check (DRY_RUN={DRY_RUN})")

    read_client = _get_read_client()

    latest_id = get_latest_tweet_id(read_client)
    if not latest_id:
        print("[SKIP] Could not fetch latest tweet ID")
        return

    replied_ids = load_replied_ids()
    if latest_id in replied_ids:
        print(f"[SKIP] Already replied to {latest_id}")
        return

    tweet_text = remaining_time()
    if tweet_text == "Ya acabó.":
        print("[SKIP] Countdown ended, not replying")
        return

    if DRY_RUN:
        print(f"[DRY RUN] Would quote tweet {latest_id}: {tweet_text[:80]}...")
        return

    write_client = _get_write_client()
    try:
        write_client.create_tweet(text=tweet_text, quote_tweet_id=latest_id)
        save_replied_id(latest_id)
        print(f"[SUCCESS] Quoted tweet {latest_id}")
    except tweepy.TweepyException as e:
        print(f"[ERROR] Failed to reply: {e}")
        raise


if __name__ == "__main__":
    main()
