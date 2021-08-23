import asvz_register
import waitforempty
import repeatedentrys
import threading
import logging
from pathlib import Path
from subprocess import Popen #

logger = logging.getLogger(__name__)
threads = []
browser = None

def onetime(classid):
    asvz_register.setuplogger(classid)
    asvz_register.register(classid, browser)
def getclassid():
    return int(input("Enter the classid (0 for exit):"))


def main():
    Path('logs').mkdir(exist_ok=True)
    logging.basicConfig(format=f'[%(levelname)s] %(asctime)s [%(threadName)s]: %(message)s',
                        datefmt='%Y-%m-%d %I:%M:%S %p')
    # logging.basicConfig()
    # logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.debug('main started')
    browser = asvz_register.initialize_browser()
    while True:
        print("Enter your Options:")
        print("1. Add a ONE-TIME-enrollement-event")
        print("2. Add a REPEATED-enrollement-event")
        print("3. OOOOPs, I forgot to enroll")
        print("4. Run Test.py")
        print("5. Exit")
        option = int(input("Enter your choice: \n"))
        if option == 1:
            classid = getclassid()
            if classid == 0:
                continue
            threads.append(threading.Thread(name=classid, target=onetime(classid)))
            threads[len(threads) - 1].start()
        if option == 2:
            classid = getclassid()
            if classid == 0:
                continue
            threads.append(threading.Thread(name=classid, target=repeatedentrys.lectionstart, args=(classid,)))
            threads[len(threads) - 1].start()
        if option == 3:
            classid = getclassid()
            if classid == 0:
                continue
            Popen["python3", "waitforempty.py " + str(classid)]
        if option == 4:
            Popen["python3", "test.py"]
        if option == 5:
            logger.critical("Exiting")
            break
        else:
            print("Unknown option")


if __name__ == "__main__":
    main()


