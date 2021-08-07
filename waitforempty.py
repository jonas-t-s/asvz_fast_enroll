import random
import sys

import asvz_register
import time
import json

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.expected_conditions import staleness_of
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime, time, date, timedelta
from time import sleep
import argparse
import tzlocal
import logging
from pathlib import Path
import requests

browser = asvz_register.initialize_browser(headless=True)


def isfree(classid):
    try:
        lesson_url = "https://schalter.asvz.ch/tn-api/api/Lessons/" + classid
        req = requests.get(lesson_url)
        text = req.text
        data = json.loads(text)
        participantsMax = data['data']['participantsMax']
        participantCount = data['data']['participantCount']
    except:
        return False # This should never happen, but if so we asume we got a timeout and therefore we should try again later
    if participantCount == participantsMax:
        return False
    else:
        return True

# Do until we recieve a break signal
while True:
    if not isfree(sys.argv[1]):
        waittime = random.randint(10,360)
        print("sleeping for " + str(waittime) + " seconds")
        sleep(waittime)
        continue
    try:
        #requests.post() Do something you want here. I post to IFTTT May be usefull if the automated register fails
        asvz_register.main()
        break
    except:
        continue
