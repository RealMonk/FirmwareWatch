import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import requests
import schedule


from lxml import html

VERSION = ''
BOT_TOKEN = '***REMOVED***'
CHAT_ID = '-899982055'
IMPLEMENTED_VERSION = ""
BASE_BOT_URL = 'https://api.telegram.org/bot%s/' % BOT_TOKEN
OFFSET = 0


# SETTING UP LOGGER
########################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

# file_handler = logging.FileHandler('./logs.log')
file_handler = RotatingFileHandler('./logs.log', maxBytes=5*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
########################################

def check_firmware():
    global VERSION
    r = requests.get('https://www.gigabyte.com/Enterprise/Rack-Server/R282-N81-rev-100#Support-Firmware')
    tree = html.fromstring(r.content)
    version_text = tree.xpath(
        '/html/body/div/div[3]/div[3]/div/main/div[1]/section[3]/div/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/text()')
    VERSION = version_text[0]
    # print(f"Recieved version from Gigabyte: {VERSION}")
    logger.info(f"Recieved version from Gigabyte: {VERSION}")


def check_version_and_notify():
    if VERSION != IMPLEMENTED_VERSION:
        text_to_send = 'Curent firmware version: ' + VERSION
        logger.info("New version (" + VERSION + ") is different from implemented version(" + VERSION + ")")
        send_mesage_to_telegram(text_to_send)

def send_mesage_to_telegram(text):
    url = '%ssendMessage?chat_id=%s' % (
        BASE_BOT_URL, CHAT_ID)
    _result = requests.post(url, json={'text': text}, timeout=10)


def get_updates(offset=None):
    method = 'getUpdates'
    params = {'offset': offset}
    response = requests.get(BASE_BOT_URL + method, params=params)
    return response.json()


def check_message():
    global OFFSET, IMPLEMENTED_VERSION
    updates = get_updates(OFFSET)

    if 'result' in updates:
        for update in updates['result']:
            OFFSET = update['update_id'] + 1

            if 'message' in update and 'text' in update['message']:
                message = update['message']['text']
                print(f"New message in channel: {message}")
                if message == '/implemented':
                    IMPLEMENTED_VERSION = VERSION
                    send_mesage_to_telegram("New implemented version: " + IMPLEMENTED_VERSION)
                    # print(f"New implemented version: {IMPLEMENTED_VERSION}")
                    logger.info("New implemented version: " + IMPLEMENTED_VERSION)



# check_firmware()
# notify_by_telegram()

# schedule.every().minute.do(check_firmware)
schedule.every(5).seconds.do(check_firmware)
schedule.every(2).seconds.do(check_message)
schedule.every(10).seconds.do(check_version_and_notify)

while True:
    schedule.run_pending()
    time.sleep(1)
