import datetime
import sys
from threading import Lock

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
threads = []
#lock: Lock = threading.Lock()
'''
This File lets you enroll repeatedly on multiple things.
usage: python repeatedentrys LECTIONID's
'''
global browser
browser = None

def lectionstart(classid):
    oldclassid = classid
    asvz_register.setuplogger(classid)
    oldclasstime = asvz_register.get_enrollment_time(oldclassid)
    print(oldclasstime[0].time(), asvz_register.get_enrollment_time(classid)[0].time())
    # If something changes, we abbort the thread.
    # browser = asvz_register.initialize_browser(headless=True)
    while oldclasstime[0].time() == asvz_register.get_enrollment_time(classid)[0].time() and oldclasstime[0].weekday() == asvz_register.get_enrollment_time(classid)[0].weekday():
        while True:
            try:
                asvz_register.register(classid)
            except:
                continue
            break
        classid = int(int(classid) + 1)
    logger.warning("The Enrollmenttime changed, so we assume something changed. Please check and restart the bot.")

def browserrestart():
    while True:
        global browser
        if datetime.now().hour == 3 and datetime.now().min == datetime.now().second == 0 and datetime.now().weekday() == 1:
            logger.debug("getting lock")
            #lock.acquire()
            logger.debug("closing browser")
            browser.close()
            logger.debug("getting new browser")
            browser = asvz_register.initialize_browser()
            logger.debug("releasing lock")
            #lock.release()
        sleep(1)




def main():
    #exec("test.py")
    # setup logger
    Path('logs').mkdir(exist_ok=True)
    logging.basicConfig(format=f'[%(levelname)s] %(asctime)s [%(threadName)s]: %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')
    #logging.basicConfig()
    #logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug('main started')
    # threads.append(threading.Thread(name="Browserrestart", target=browserrestart))
    #For every lesson we want to attend we create a seperate thread (note that those sleep almost always
    for arg in sys.argv:
        #test if the argument is a digit. (we note that this should only fail for sys.argv[0], which is the scriptname
        if arg.isdigit():
            j = asvz_register.get_data_about_lesson(arg)
            sportname=j["sportName"]
            when = datetime.strptime(j["starts"], "%Y-%m-%dT%H:%M:%S%z")
            day =["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            name = sportname + "-" + day[when.weekday()] + "(orig:" + arg +")"
            threads.append(threading.Thread(name=name, target=lectionstart, args=(arg,)))
            logger.info("Thread with arg: "+ str(arg) + " started")
        else:
            logger.info(arg + " is not a valid digit. Proceeding to the next one.")
    #log and start the threads
    global browser
    #browser = asvz_register.initialize_browser(headless=True)
    i = 1
    #browserrestarter= threading.Thread(name="browserrestarter", target=browserrestart)
    #threads.append(browserrestarter)
    for thread in threads:
        thread.start()
        logger.debug("Thread number " + str(i) + " of " + str(len(threads)) + " started" )
        i = i + 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.critical("KeyboardInterupt recieved. Shutting down")
        if browser is not None:
            browser.close()
