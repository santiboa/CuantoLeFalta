"""Bot que postea regularmente cuanto le falta a Claudia Sheinbaum"""
# Import required libraries
import datetime
import json
import time
from datetime import timedelta
from pathlib import Path
from random import random

import tweepy
from dotenv import load_dotenv

load_dotenv()

from countdown import end, remaining_time, start, timezone
from milestones import MilestoneChecker
import president_reply
import os
import random as random_module

LATEST_TWEET_FILE = Path(__file__).parent / "latest_tweet.json"

# President reply: set REPLIES=on in .env to enable
REPLIES_ENABLED = os.getenv("REPLIES", "off").lower() == "on"
REPLY_POLL_INTERVAL_MINUTES = 30
REPLY_HOUR_START = 7
REPLY_HOUR_END = 22  # 10 PM



def save_latest_tweet(tweet_id: str, tweet_text: str) -> None:
    """Save the latest posted tweet ID and text for the webapp to display."""
    data = {
        "tweet_id": str(tweet_id),
        "tweet_text": tweet_text,
        "posted_at": datetime.datetime.now(timezone).isoformat(),
    }
    with open(LATEST_TWEET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Global DRY_RUN flag - set DRY_RUN=false in .env to actually post tweets
DRY_RUN = os.getenv("DRY_RUN", "true").lower() != "false"

#Important Keys (Make sure to secure your keys if this is production)
consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')
access_token = os.getenv('ACCESS_TOKEN')
access_token_secret = os.getenv('ACCESS_TOKEN_SECRET')

client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)


# Tweet timing: random interval between 24 and 36 hours, avoiding midnight-6AM CDMX
QUIET_HOUR_START = 2   # 2 AM
QUIET_HOUR_END = 7     # 7 AM
QUIET_RANDOM_OFFSET_MIN = 60  # max minutes of random offset after quiet hours end


def nextTweetCalc():
    # Random interval between 24 and 36 hours
    periodicalTime = 60 * 60 * (24 + 12 * random())
    nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=periodicalTime)

    # If it lands in quiet hours (midnight-6AM), push to 6AM + random offset
    if QUIET_HOUR_START <= nextTweetTime.hour < QUIET_HOUR_END:
        nextTweetTime = nextTweetTime.replace(hour=QUIET_HOUR_END, minute=0, second=0)
        nextTweetTime += timedelta(minutes=random_module.randint(0, QUIET_RANDOM_OFFSET_MIN))
        periodicalTime = (nextTweetTime - datetime.datetime.now(timezone)).total_seconds()

    nextTweetTimeStr = f"Next tweet in {round(periodicalTime/3600, 2)} hours, or at {nextTweetTime.strftime('%Y-%m-%d %H:%M:%S')} Mexico City time."
    print(nextTweetTimeStr)
    return periodicalTime

# Initialize tweet cycle
periodicalTime = nextTweetCalc()

# Show what the next tweet will look like (never post on startup)
tweet = remaining_time()
print(f'[STARTUP] Next tweet will be: {tweet}')

# Initialize next tweet time
nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=nextTweetCalc())

# Initialize milestone checker
milestone_checker = MilestoneChecker(client, start, end, timezone, dry_run=DRY_RUN)

# President reply: track last poll time
last_reply_poll = None
if REPLIES_ENABLED:
    print(f"[REPLY] Polling every {REPLY_POLL_INTERVAL_MINUTES} min between {REPLY_HOUR_START}:00-{REPLY_HOUR_END}:00 CDMX")
else:
    print("[REPLY] Disabled (set REPLIES=on in .env to enable)")

while True:
    time.sleep(60)  # Wait 1 minute

    # Check if the current time is after the next tweet time
    now = datetime.datetime.now(timezone)

    # President reply: poll every 30 minutes during active hours
    in_reply_window = REPLY_HOUR_START <= now.hour < REPLY_HOUR_END
    minutes_since_last_poll = (
        (now - last_reply_poll).total_seconds() / 60 if last_reply_poll else float("inf")
    )

    if REPLIES_ENABLED and in_reply_window and minutes_since_last_poll >= REPLY_POLL_INTERVAL_MINUTES:
        president_reply.DRY_RUN = DRY_RUN
        last_reply_poll = now
        try:
            president_reply.main()
        except Exception as e:
            print(f"[REPLY ERROR] {e}")

    # Check milestones first (immediate posting if detected)
    milestone_checker.check_and_tweet(now)

    # For DEBUG:
    # print(f'Time right now: {now}')
    if now >= nextTweetTime:
        tweet = remaining_time()
        if tweet == "Ya acabó.":
            if DRY_RUN:
                print("[DRY RUN] TWEET INCOMING (of the end though!)")
            else:
                # client.create_tweet(text=tweet)
                print("TWEET INCOMING (of the end though!)")
            print(tweet)
            # break  # Stop the loop when countdown is over
        else:
            if DRY_RUN:
                print("[DRY RUN] TWEET INCOMING!")
                print(f'[DRY RUN] TWEET: {tweet}')
            else:
                response = client.create_tweet(text=tweet)
                save_latest_tweet(response.data["id"], tweet)
                print("TWEET INCOMING!")
                print(tweet)

        # Calculate the next tweet time after sending the current one
        periodicalTime = nextTweetCalc()
        nextTweetTime = now + timedelta(seconds=periodicalTime)

        # Print when the next tweet will happen
        nextTweetTimeStr = f"Next tweet will be at {nextTweetTime.strftime('%Y-%m-%d %H:%M:%S')} Mexico City time."
        print(nextTweetTimeStr)
    # else: #for DEBUG
    #     print(f'I said next tweet is on {nextTweetTime}')