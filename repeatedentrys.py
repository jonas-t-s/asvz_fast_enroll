import datetime
import sys

import asvz_register
import threading
import time
import test

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

logger = logging.getLogger(__name__)

'''
This File lets you enroll repeatedly on multiple things.
usage: python repeatedentrys LECTIONID's
'''


def lectionstart(classid):
    oldclassid = classid
    asvz_register.setuplogger(classid)
    oldclasstime = asvz_register.get_enrollment_time(oldclassid)
    print(oldclasstime[0].time, asvz_register.get_enrollment_time(classid)[0].time)
    while oldclasstime[0].time() == asvz_register.get_enrollment_time(classid)[0].time() and oldclasstime[0].weekday() == asvz_register.get_enrollment_time(classid)[0].weekday():
        logger.critical("Test")
        while True:
            try:
                asvz_register.register(classid)
            except:
                continue
            break
        classid = int(int(classid) + 1)
    logger.warning("The Enrollmenttime changed, so we assume something changed. Please check and restart the bog.")


def main():
    #exec("test.py")
    Path('logs').mkdir(exist_ok=True)
    logging.basicConfig(format=f'[MAIN] %(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug('main started')
    threads = []
    for arg in sys.argv:
        if arg.isdigit():
            threads.append(threading.Thread(target=lectionstart, args=(arg,)))
            logger.info("Thread with arg: "+ str(arg) + " started")
        else:
            logger.info(arg + " is not a valid digit. Proceeding to the next one.")
    i = 1
    for thread in threads:
        thread.start()
        logger.debug("Thread number " + str(i) + " of " + str(len(threads)) + " started" )
        i = i + 1


if __name__ == "__main__":
    main()
