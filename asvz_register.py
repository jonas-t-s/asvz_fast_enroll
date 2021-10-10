import json
import threading

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


def load_credentials():
    try:
        with open("credentials.json", 'r') as fp:
            j = json.load(fp)
        return j['username'], j['password']
    except FileNotFoundError:
        print(
            "put your credentials {username:your_username, password: your_password} into a file named credentials.json")
    except json.JSONDecodeError:
        print("your credentials.json is malformed make sure to have all keys and values doubly quoted")


def initialize_browser(headless=True):
    try:
        options = FirefoxOptions()
        options.headless = headless
        browser = webdriver.Firefox(options=options)
    except Exception:
        options = ChromeOptions()
        options.headless = headless
        browser = webdriver.Chrome(options=options)
    return browser


def login(usernameInput, passwordInput, existing_browser=None, lessonid=None):


    if existing_browser is None:
        browser = initialize_browser()
    else:
        browser = existing_browser
    try:

        browser.implicitly_wait(30)

        def wait_for_xpath(xpath, timeout=30):
            return WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath)))

        if lessonid is None:
            # lesson_url = "https://auth.asvz.ch/account/login"
            # lesson_url = "https://schalter.asvz.ch/tn/lessons/119157"
            lesson_url = "https://schalter.asvz.ch/tn/lessons/218642"
        else:
            lesson_url = "https://schalter.asvz.ch/tn/lessons/" + str(lessonid)

        browser.get(lesson_url)
        if not existing_browser is None:
            browser.refresh() # It could be possible, that the cache and the authentification is not up to date here. So we reload. (This may only happen, if the browser is created before.)

        if 'Authorization' in browser.requests[-1].headers:
            # logged in
            return browser.requests[-1].headers
        redirect_button = wait_for_xpath(
            "//button[contains(@title,\"Login\")]")
        #redirect_button = browser.find_element_by_xpath("//button[contains(@title,\"Login\")]")
        redirect_button.click()

        AAI_button = wait_for_xpath(
            "//button[@value=\"SwitchAai\"]")
        AAI_button.click()

        session_memory = browser.find_element_by_xpath(
            ".//*[@id='rememberForSession']")
        
        session_memory.click()
       

        Uni_list = browser.find_element_by_xpath(
            ".//*[@id='userIdPSelection_iddwrap']")
        Uni_list.click()

        # hover ETH option and click it
        ActionChains(browser).move_to_element(Uni_list).move_to_element(
            browser.find_element_by_xpath(".//*[contains(@title, 'ETH')]")).click().perform()

        username = WebDriverWait(browser, 15).until(
            EC.presence_of_element_located((By.ID, "username")))

        username.send_keys(usernameInput)

        password = browser.find_element_by_id('password')
        password.send_keys(passwordInput)

        # keep a reference to the login page submit button
        old_submit_button = browser.find_element_by_xpath(
            ".//*[@type='submit']")

        password.send_keys(Keys.RETURN)

        # Wait for new page to be loaded
        WebDriverWait(browser, 15).until(
            staleness_of(old_submit_button)
        )

        for i in range(15):
            if 'Authorization' in browser.requests[-1].headers:
                # logged in
                break
            else:
                # if we need to accept information sent to asvz
                try:
                    browser.implicitly_wait(1)
                    wait_for_xpath(".//*[@value='Accept']", timeout=1)
                    accept_button = browser.find_element_by_xpath(
                        ".//*[@value='Accept']")
                    accept_button.click()
                except TimeoutException as e:
                    pass

    finally:
        if existing_browser is None:
            browser.close()
    return browser.requests[-1].headers


error_msgs = {
    "Das Angebot ist schon ausgebucht.": "full",
    "Der Anmeldeschluss liegt in der Vergangenheit - eine Anmeldung ist leider nicht mehr möglich!": "past",
    "Diese Lektion wurde abgesagt - eine Einschreibung ist leider nicht möglich!": "canceled",
    "Der Anmeldebeginn liegt in der Zukunft - eine Anmeldung ist leider noch nicht möglich!": "future"
}


def enroll(headers, lesson_id):
    res = requests.post(
        f'https://schalter.asvz.ch/tn-api/api/Lessons/{lesson_id}/enroll', headers=headers)

    if res.status_code == 201:
        return None, json.loads(res.content.decode())['data']['placeNumber']
    if res.status_code == 422:
        message = json.loads(res.content.decode())['errors'][0]['message']
        assert message in error_msgs
        return message, None

def get_data_about_lesson(lesson_id):
    req = requests.get(
        f"https://schalter.asvz.ch/tn-api/api/Lessons/{lesson_id}")
    j = json.loads(req.content.decode())
    return j['data']

def get_enrollment_time(lesson_id):
    j = get_data_about_lesson(lesson_id)
    def parse_time(s): return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
    return parse_time(j['enrollmentFrom']), parse_time(j['enrollmentUntil'])


def now():
    local_tz = tzlocal.get_localzone()
    now = datetime.now()
    return now.astimezone(local_tz)


def register(classid, existingBrowser=None, lock=threading.Lock):
    username, password = load_credentials()
    # get enrollment start time
    logger.debug("starting to get register time")
    fr, to = get_enrollment_time(classid)

    # sleep until 1 minutes before registration opens
    time_to_sleep = max(0, (fr-now()).total_seconds()-90)
    sleeptime = (fr - timedelta(minutes=1,seconds=30))
    logger.info(f"sleep for {time_to_sleep} seconds until {sleeptime}, we then start logging in")
    sleep(time_to_sleep)


    logger.info("getting lock")
    # lock.acquire()
    # login
    logger.info("logging in")
    headers = login(username, password, existingBrowser, lessonid=classid)
    #lock.release()
    logger.debug("releasing lock")
    err1, val1 = enroll(headers, classid) # We test here, if it breaks or not. If it breaks, we enforce automatically a restart.
    # sleep until 3 s before registration opens
    time_to_sleep = max(0, (fr-now()).total_seconds()-3)
    logger.info(f"sleep for {time_to_sleep} seconds until {fr}")
    sleep(time_to_sleep)
    sleeptime_in_loop = 1
    for i in range(15):
        err, val = enroll(headers, classid) # We expect a typeerror here. If this happens, we break immediately
        if err in error_msgs and error_msgs[err] != "future":
            raise Exception(err)
        if err is None:
            logger.debug(f"Successfully registered with place number {val}")
            return
        logger.info(f"tried enrolling but not open yet")
        sleep(sleeptime_in_loop)
        if i >= 2:
            sleeptime_in_loop = sleeptime_in_loop/1.5
    raise Exception("This should never happen")

def setuplogger(classid):
    logging.basicConfig(format=f'[{classid}] %(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug('logger set up')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('classid', help="id of class you want to register for")
    args = parser.parse_args()
    Path('logs').mkdir(exist_ok=True)
    setuplogger(args.classid)
    browser = initialize_browser(headless=True)
    #it is planned, that this loop only runs once, but in my testing I've seen, that it is possible, that the user get unauthorized and then we restart. (and lose approx 20 seconds)
    while True:
        try:
            register(args.classid, browser)
        except TypeError:
            logger.exception("A TypeError occurred, we try again")
            continue
        break
    browser.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.critical("KeyboardInterupt received. Shutting down")