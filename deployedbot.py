"""Bot que postea regularmente cuanto le falta a Claudia Sheinbaum"""
# Import required libraries
import tweepy
import datetime
from datetime import timedelta
import time
from random import random
import pytz
from calendar import monthrange

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

timezone = pytz.timezone("America/Mexico_City")

# Correct datetime initialization for start and end dates with tz-aware format.
end = timezone.localize(datetime.datetime(year=2030, month=10, day=1, hour=0, minute=0, second=0))
start = timezone.localize(datetime.datetime(year=2024, month=10, day=1, hour=0, minute=0, second=0))

def remainingTime():
    # Get the current time in Mexico City timezone
    now = datetime.datetime.now(timezone)

    # Calculate the difference between 'now' and 'end'
    diffTime = end - now

    # Ensure the time difference is correct and positive
    if diffTime.total_seconds() <= 0:
        return "Ya acabó."

    sexenio = end - start
    elapsedT = now - start

    # Calculate elapsed percentage and remaining days
    elapsedTimePercent = (elapsedT.total_seconds() / sexenio.total_seconds()) * 100
    elapsedTimePercent = f"{elapsedTimePercent:.3f}"
    elapsedDays = elapsedT.days
    remainingDays = diffTime.days

    # Calculate total hours, minutes, and seconds more accurately
    total_seconds = diffTime.total_seconds()
    total_hours = total_seconds // 3600
    minutes = round((total_seconds % 3600) // 60)  # Round minutes
    seconds = round(total_seconds % 60)            # Round seconds
    hours = int(total_hours % 24)  # Modulo 24 to get the leftover hours after full days

    # Calendar-style countdown: years, months, days (until end of current month)
    # People think in calendar terms - days left in this month, months until target month
    years = remainingDays // 365
    months = ((end.year - now.year) * 12 + end.month - now.month - 1) % 12
    endday = monthrange(now.year, now.month)  # returns tuple (weekday, num_days)
    days = endday[1] - now.day  # days until end of current month

    # Create text parts with singular/plural formatting
    yearsText = " año" if years == 1 else " años"
    monthsText = " mes" if months == 1 else " meses"
    daysText = " día" if days == 1 else " días"
    hoursText = " hora" if hours == 1 else " horas"
    minutesText = " minuto" if minutes == 1 else " minutos"
    secondsText = " segundo" if seconds == 1 else " segundos"

    elapsedDaysText = f'Ya pasó {elapsedTimePercent}% del sexenio ({elapsedDays} días). #cuantolefalta'
    remainingDaysText = f'(o bien, {remainingDays} días). '

    # Debugging info to check what is happening with the time calculation
    print(f"Now: {now}, End: {end}, Difference: {diffTime}, Timezone: {now.tzinfo}")

    # Format the status
    status = f"Le faltan {years}{yearsText}, {months}{monthsText}, {days}{daysText}, {hours}{hoursText}, {minutes}{minutesText}, {seconds}{secondsText} {remainingDaysText} {elapsedDaysText}"
    return status

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
tweet = remainingTime()
client.create_tweet(text=tweet)
print(f'Sample tweet right now at start of this:{tweet}')

# Initialize next tweet time
nextTweetTime = datetime.datetime.now(timezone) + timedelta(seconds=nextTweetCalc())

while True:
    time.sleep(60)  # Wait 1 minute

    # Check if the current time is after the next tweet time
    now = datetime.datetime.now(timezone)
    # For DEBUG:
    # print(f'Time right now: {now}')
    if now >= nextTweetTime:
        tweet = remainingTime()
        if tweet == "Ya acabó.":
            # client.create_tweet(text=tweet)
            print("TWEET INCOMING (of the end though!)")
            print(tweet)
            # break  # Stop the loop when countdown is over
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