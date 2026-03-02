"""Bot que postea regularmente cuanto le falta a Claudia Sheinbaum"""
# Import required libraries
import datetime
import time
from datetime import timedelta
from random import random

import tweepy

from countdown import end, remaining_time, start, timezone
from milestones import MilestoneChecker

# Global DRY_RUN flag - set to True to log tweets instead of posting to API
DRY_RUN = True

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
    # Random interval between 3 and 8 hours
    periodicalTime = max(60 * 60 * 7, 60 * 60 * 13 * random())
    nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=periodicalTime)
    nextTweetTimeStr = f"Next tweet in {round(periodicalTime/3600, 2)} hours, or at {nextTweetTime.strftime('%Y-%m-%d %H:%M:%S')} Mexico City time."
    print(nextTweetTimeStr)
    return periodicalTime

# Initialize tweet cycle
periodicalTime = nextTweetCalc()

#Sample DEBUG:
tweet = remaining_time()
if DRY_RUN:
    print(f'[DRY RUN] TWEET: {tweet}')
else:
    client.create_tweet(text=tweet)
print(f'Sample tweet right now at start of this:{tweet}')

# Initialize next tweet time
nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=nextTweetCalc())

# Initialize milestone checker
milestone_checker = MilestoneChecker(client, start, end, timezone, dry_run=DRY_RUN)

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
                client.create_tweet(text=tweet)
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