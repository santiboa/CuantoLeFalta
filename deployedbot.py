"""Bot que postea regularmente cuanto le falta a Claudia Sheinbaum"""
# Import required libraries
import datetime
import json
import time
from datetime import timedelta
from pathlib import Path
from random import random

import tweepy

from countdown import end, remaining_time, start, timezone
from milestones import MilestoneChecker
import os

LATEST_TWEET_FILE = Path(__file__).parent / "latest_tweet.json"


def save_latest_tweet(tweet_id: str, tweet_text: str) -> None:
    """Save the latest posted tweet ID and text for the webapp to display."""
    data = {
        "tweet_id": str(tweet_id),
        "tweet_text": tweet_text,
        "posted_at": datetime.datetime.now(timezone).isoformat(),
    }
    with open(LATEST_TWEET_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Global DRY_RUN flag - set to True to log tweets instead of posting to API
DRY_RUN = True

# #region agent log
import json
with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
    f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"A","location":"deployedbot.py:14","message":"DRY_RUN flag value","data":{"DRY_RUN":DRY_RUN},"timestamp":int(__import__('time').time()*1000)}) + '\n')
# #endregion

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


# Function to calculate next tweet interval
def nextTweetCalc():
    # Random interval between 8 and 24 hours
    periodicalTime = max(60 * 60 * 8, 60 * 60 * 24 * random())
    nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=periodicalTime)
    nextTweetTimeStr = f"Next tweet in {round(periodicalTime/3600, 2)} hours, or at {nextTweetTime.strftime('%Y-%m-%d %H:%M:%S')} Mexico City time."
    print(nextTweetTimeStr)
    return periodicalTime

# Initialize tweet cycle
periodicalTime = nextTweetCalc()

#Sample DEBUG:
tweet = remaining_time()
# #region agent log
import json
with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
    f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"B","location":"deployedbot.py:43","message":"Before DRY_RUN check","data":{"DRY_RUN":DRY_RUN,"tweet_length":len(tweet)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
# #endregion
if DRY_RUN:
    print(f'[DRY RUN] TWEET: {tweet}')
    # #region agent log
    import json
    with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
        f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"B","location":"deployedbot.py:48","message":"DRY_RUN branch taken","data":{"branch":"dry_run"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
else:
    response = client.create_tweet(text=tweet)
    save_latest_tweet(response.data["id"], tweet)
    # #region agent log
    import json
    with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
        f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"B","location":"deployedbot.py:52","message":"API branch taken","data":{"branch":"api"},"timestamp":int(__import__('time').time()*1000)}) + '\n')
    # #endregion
print(f'Sample tweet right now at start of this:{tweet}')

# Initialize next tweet time
nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=nextTweetCalc())

# Initialize milestone checker
# #region agent log
import json
with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
    f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"C","location":"deployedbot.py:54","message":"Creating MilestoneChecker","data":{"DRY_RUN":DRY_RUN,"dry_run_param":DRY_RUN},"timestamp":int(__import__('time').time()*1000)}) + '\n')
# #endregion
milestone_checker = MilestoneChecker(client, start, end, timezone, dry_run=DRY_RUN)
# #region agent log
import json
with open('/Users/santiagopadilla/Documents/CuantoLeFalta/.cursor/debug-bab3a6.log', 'a') as f:
    f.write(json.dumps({"sessionId":"bab3a6","runId":"initial","hypothesisId":"C","location":"deployedbot.py:60","message":"MilestoneChecker created","data":{"milestone_checker_dry_run":milestone_checker.dry_run},"timestamp":int(__import__('time').time()*1000)}) + '\n')
# #endregion

while True:
    time.sleep(60)  # Wait 1 minute

    # Check if the current time is after the next tweet time
    now = datetime.datetime.now(timezone)
    
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