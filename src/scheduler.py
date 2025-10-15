from tools.feedback_requests import checkUnprocessedFeedbackRequests

import schedule
import time


def setupSchedule() -> None:
    schedule.every().hour.at(':00').do(checkUnprocessedFeedbackRequests)

def runSchedule():
    setupSchedule()
    while True:
        schedule.run_pending()
        time.sleep(1)
