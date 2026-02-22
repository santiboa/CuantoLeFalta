#!/bin/env python3.7
# This little script posts once whenever you run it.
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
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAPuoKgEAAAAA2eqjAlpwZi6OqvUGjPLVQkDaGYU%3DZaBld7KnQr9EKHXdYUFgghfQ7f5sX6q0fkFrLNImpKJAMlaaDv'

# auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
# auth.set_access_token(access_token, access_token_secret)

# auth = tweepy.OAuth2BearerHandler(bearer_token)

client = tweepy.Client (
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret
)

#Auth settings store in single API
# api = tweepy.API(auth)

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
    elapsedDaysText = f' Ya pasó {elapsedTimePercent}% del sexenio ({elapsedDays} días).'
    remainingDaysText = f' (o bien, {remainingDays} días).'

    #Putting it all together in a string. If you want to return a different line use '\n' for python print(), but tweepy might not take it. Ej: "Feliz día del contador a todos los contadores! Siempre podrán contar conmigo.\n\n" +
    status = "Le falta "+ years + yearsText + months + monthsText + days + daysText + hours + hoursText + minutes + minutesText + seconds + secondsText + remainingDaysText + elapsedDaysText
    #print("Latest status is: ", status)
    return status

tweetToPublish = remainingTime()
client.create_tweet(text=tweetToPublish) #uncomment this to actually publish a tweet

print("Just tweeted: '" + tweetToPublish + "' - this script only runs once.")
