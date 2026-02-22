#!/usr/local/python3.7
# Replies to mentions, AMLO's latest tweets, and posts periodically
# Import Tweety and date / times
import tweepy
import datetime
from datetime import timedelta
import time
import math
from random import random
import pytz
from calendar import monthrange

#Important Keys
consumer_key = 'fNP3wN6zG2W4PiGETsaFU7Bwi'
consumer_secret = 'Tz1HjLXiXdb5Gn9uP2IXocrbLut4fHCOF5EhR1vUOvnHOzvP8F'
access_token = '1338193765656264704-FmIfbY97zBxyY0qaNxecI9MmCJUsUv'
access_token_secret = '4UK79svSne8789YiXwwrXGnX2FaC2OeuEeZvIJxyrT3RY'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

#Auth settings store in single API
api = tweepy.API(auth)

tweetToPublish = "Achis. Perame deja checo."
timezone = pytz.timezone("America/Mexico_City")

def remainingTime():
    #getting date info and putting it in the right timezone
    now = datetime.datetime.now()
    end = datetime.datetime(year = 2024, month = 10, day = 1, hour = 7, minute = 0, second = 0)
    start = datetime.datetime(year = 2018, month = 12, day = 1, hour = 7, minute = 0, second = 0)
    #tester = datetime.datetime(year = 2021, month = 1, day = 1, hour = 7, minute = 0, second = 0)
    #tester = timezone.localize(tester)
    start = timezone.localize(start)
    now = timezone.localize(now)
    end = timezone.localize(end)

    diffTime = end - now
    sexenio = end - start
    elapsedT = now - start

    elapsedTimePercent = ( (elapsedT.seconds + elapsedT.days*24*3600) / (sexenio.seconds + sexenio.days*24*3600) * 100)
    elapsedTimePercent = str("{:.2f}".format(elapsedTimePercent))           #changing the float to a more manageable XX.XX % (two decimal places)
    elapsedDays = elapsedT.days
    remainingDays = diffTime.days

    #print(elapsedDays)
    #print(elapsedTimePercent)
    #print(tester)

    #taking out the right time values
    years = ((end.year - now.year)*12 + end.month - now.month - 1) / 12
    years = math.floor(years)
    months = ((end.year - now.year)*12 + end.month - now.month - 1) % 12
    #days till end of month
    endday = monthrange(now.year, now.month)  #returns a touple
    days = endday[1] - now.day #days till end of month
    hours = math.floor(diffTime.seconds / 3600)
    minutes = math.floor(diffTime.seconds % 3600 / 60)
    seconds = math.floor(diffTime.seconds % 3600 % 60)

    #checking out if plural or singular
    yearsText = " años, "
    if years == 1:
        yearsText = " año, "
    monthsText = " meses, "
    if months == 1:
        monthsText = " mes, "
    daysText = " días, "
    if days == 1:
        daysText = " día, "
    hoursText = " horas, "
    if hours == 1:
        hoursText = " hora, "
    minutesText= " minutos y "
    if minutes == 1:
        minutesText = " minuto y "
    secondsText = " segundos"
    if seconds == 1:
        secondsText = " segundo"

    #converting to string
    years = str(years)
    months = str(months)
    days = str(days)
    hours = str(hours)
    minutes = str(minutes)
    seconds = str(seconds)
    elapsedDaysText = f' Ya pasó {elapsedTimePercent}% del sexenio ({elapsedDays} días). #cuantolefalta'
    remainingDaysText = f' (o bien, {remainingDays} días). '

    #Putting it all together in a string. If you want to return a different line use '\n' for python print(), but tweepy might not take it.
    #You'd need to save it to a text file first, and then pass that as the string for tweepy
    status = "Le falta " + years + yearsText + months + monthsText + days + daysText + hours + hoursText + minutes + minutesText + seconds + secondsText + remainingDaysText + elapsedDaysText
    #print("Latest status is: ", status)
    return status

fileName = 'last_seen_id.txt'
loopCount = 0
periodicalCount = 0

#next tweet calculation, inital setup
periodicalTime = max(random()*8*60*60, 6*60*60)

#function to calculate when next tweet will happen)
def nextTweetCalc(periodicalTime):
    nextTweetHrs = round(periodicalTime/3600,2)
    nextTweetHrs = str(nextTweetHrs)
    nextTweetTime = datetime.datetime.now() + timedelta(seconds = periodicalTime)
    nextTweetTime = timezone.localize(nextTweetTime)
    global nextTweetTimeStr
    nextTweetTimeStr = "Next periodical tweet in " + nextTweetHrs + ' hours, or at ' + str(nextTweetTime)
    print(nextTweetTimeStr)
    return

nextTweetCalc(periodicalTime)

# good guide: https://www.youtube.com/watch?v=W0wWwglE1Vc&ab_channel=CSDojo

while True:
    waitTime = 60
    periodicalCount += waitTime

    #Post a periodical tweet (after a while)
    if periodicalCount > periodicalTime:
        tweetToPublish = remainingTime()
        api.update_status(tweetToPublish)

        #reset counters
        periodicalCount = 0
        periodicalTime = max(random()*24*59*61, 17*59*63) #max helps set a minimum random-looking time between tweets

        #Communicate when the next tweet is coming
        nextTweetCalc(periodicalTime)
    time.sleep(waitTime)
