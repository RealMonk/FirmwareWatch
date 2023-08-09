import enum
import json
import logging
import sys
import time
from logging.handlers import RotatingFileHandler

import requests
import schedule
from lxml import html
from memory import Memory

mem = Memory()
mem.init_db()

BOT_TOKEN = '6687794130:AAHHw3QTGSHiYwAQuDHUCg75GxT-1hsWbfs'
BASE_BOT_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
UPDATE_OFFSET = 0

BMC_VERSION = ''
BIOS_VERSION = ''
BMC_IMPLEMENTED_VERSION = "None"
BIOS_IMPLEMENTED_VERSION = "None"
BMC_XPATH = '/html/body/div/div[3]/div[3]/div/main/div[1]/section[3]/div/div[2]/div[2]/div[4]/div/div[2]/div[2]/div[2]/text()'
BIOS_XPATH = '/html/body/div/div[3]/div[3]/div/main/div[1]/section[3]/div/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/text()'


class Commands(enum.StrEnum):
    START_COMMAND = 'start'
    STOP_COMMAND = 'stop'
    HELP_COMMAND = 'help'
    CHECK_COMMAND = 'check'
    BMC_IMPLEMENTED_COMMAND = 'bmc_implemented'
    BIOS_IMPLEMENTED_COMMAND = 'bios_implemented'


BOT_COMMANDS = [{'command': Commands.START_COMMAND, 'description': 'Subscribe to recieive update notifications'},
                {'command': Commands.STOP_COMMAND, 'description': 'Unsubscribe to stop recieving update notifications'},
                {'command': Commands.CHECK_COMMAND, 'description': 'Check current version'},
                {'command': Commands.BMC_IMPLEMENTED_COMMAND, 'description': 'set current BMC version as implemented'},
                {'command': Commands.BIOS_IMPLEMENTED_COMMAND, 'description': 'set current BIOS version as implemented'},
                {'command': Commands.HELP_COMMAND, 'description': 'Show help'}]
print(BOT_COMMANDS)
# help_message = """
# /start - to start receiving update notifications
# /stop - to stop receiving update notifications
# /BMC_implemented - to set latest implemented BMC version
# /BIOS_implemented - to set latest implemented BIOS version
# """
help_message = ""
for i in BOT_COMMANDS:
    help_message += f"/{i['command']} - {i['description']}\n"

# SETTING UP LOGGER
########################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

# file_handler = logging.FileHandler('./logs.log')
file_handler = RotatingFileHandler('./logs.log', maxBytes=5 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


########################################

def check_firmware():
    global BMC_VERSION
    global BIOS_VERSION
    r = requests.get('https://www.gigabyte.com/Enterprise/Rack-Server/R282-N81-rev-100')
    tree = html.fromstring(r.content)
    BMC_VERSION = tree.xpath(BMC_XPATH)[0]
    BIOS_VERSION = tree.xpath(BIOS_XPATH)[0]
    logger.info(f"Received BMC version from Gigabyte: {BMC_VERSION}")
    logger.info(f"Received BIOS version from Gigabyte: {BIOS_VERSION}")


def check_version_and_notify():
    if BMC_VERSION != BMC_IMPLEMENTED_VERSION:
        bmc_text_to_send = (
            f'New BMC version ({BMC_VERSION}) is different from implemented version({BMC_IMPLEMENTED_VERSION})')
        logger.info(bmc_text_to_send)
        sent_message_to_all(bmc_text_to_send)

    if BIOS_VERSION != BIOS_IMPLEMENTED_VERSION:
        bios_text_to_send = (
            f'New BIOS version ({BIOS_VERSION}) is different from implemented version({BIOS_IMPLEMENTED_VERSION})')
        logger.info(bios_text_to_send)
        sent_message_to_all(bios_text_to_send)


def check_version_and_notify_specific_user(chat_id):
    if BMC_VERSION != BMC_IMPLEMENTED_VERSION:
        bmc_text_to_send = (
            f'New BMC version ({BMC_VERSION}) is different from implemented version({BMC_IMPLEMENTED_VERSION})')
        logger.info(bmc_text_to_send)
        send_message_to_specific_user(chat_id, bmc_text_to_send)

    if BIOS_VERSION != BIOS_IMPLEMENTED_VERSION:
        bios_text_to_send = (
            f'New BIOS version ({BIOS_VERSION}) is different from implemented version({BIOS_IMPLEMENTED_VERSION})')
        logger.info(bios_text_to_send)
        send_message_to_specific_user(chat_id, bios_text_to_send)


def send_message_to_specific_user(chat_id, text):
    url = f'{BASE_BOT_URL}/sendMessage?chat_id={chat_id}'
    _result = requests.post(url, json={'text': text}, timeout=10)


def sent_message_to_all(text_to_send):
    chat_list = mem.get_all_users()
    print(chat_list)

    for user in chat_list:
        send_message_to_specific_user(user[0], text_to_send)


def get_updates(offset=None):
    method = '/getUpdates'
    params = {'offset': offset}
    response = requests.get(BASE_BOT_URL + method, params=params)
    return response.json()


def set_available_commands():
    method = '/setMyCommands'
    params = {'commands': BOT_COMMANDS}
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/setMyCommands?commands=' + str(json.dumps(BOT_COMMANDS))
    # response = requests.get(BASE_BOT_URL + method, params=params)
    response = requests.get(send_text)
    print(response)


def react_on_commands():
    global UPDATE_OFFSET, BMC_IMPLEMENTED_VERSION, BIOS_IMPLEMENTED_VERSION, START_COMMAND, \
        STOP_COMMAND, HELP_COMMAND, CHECK_COMMAND, BMC_IMPLEMENTED_COMMAND, BIOS_IMPLEMENTED_COMMAND
    updates = get_updates(UPDATE_OFFSET)

    if 'result' in updates:
        for update in updates['result']:
            UPDATE_OFFSET = update['update_id'] + 1
            if 'message' in update and 'text' in update['message']:
                chat_id = update['message']['chat']['id']
                user = mem.get_user(chat_id)
                message_text = update['message']['text']
                user_name = update['message']['from']['username']
                print(message_text)
                match message_text[1:]:  # skipping '/'
                    case Commands.START_COMMAND:
                        if user is None:
                            mem.add_user(chat_id, user_name)
                            send_message_to_specific_user(chat_id,
                                                     f'Welcome, {user_name}! You have been added to the user list.')
                            logger.info(str(chat_id) + f' Welcome, {user_name}! You have been added to the user list.')
                            check_version_and_notify_specific_user(chat_id)
                    case Commands.STOP_COMMAND:
                        if user is not None:
                            mem.delete_user(chat_id)
                            send_message_to_specific_user(chat_id,
                                                     f'Goodbye, {user_name}! You have been deleted from the user list.')
                            logger.info(
                                str(chat_id) + f' Goodbye, {user_name}! You have been deleted from the user list.')
                    case Commands.CHECK_COMMAND:
                        logger.info(f'Checking and notifying specially for {user_name} chat_id: {chat_id}. ')
                        check_version_and_notify_specific_user(chat_id)
                    case Commands.BMC_IMPLEMENTED_COMMAND:
                        BMC_IMPLEMENTED_VERSION = BMC_VERSION
                        logger.info("New implemented BMC version: " + BMC_IMPLEMENTED_VERSION)
                        sent_message_to_all('New implemented BMC version: ' + BMC_IMPLEMENTED_VERSION)
                    case Commands.BIOS_IMPLEMENTED_COMMAND:
                        BIOS_IMPLEMENTED_VERSION = BIOS_VERSION
                        logger.info("New implemented BIOS version: " + BIOS_IMPLEMENTED_VERSION)
                        sent_message_to_all('New implemented BIOS version: ' + BIOS_IMPLEMENTED_VERSION)
                    case Commands.HELP_COMMAND:
                        logger.info("Displaying help")
                        send_message_to_specific_user(chat_id, help_message)
                    case _:
                        logger.info(f"No such command: {message_text}")
                        send_message_to_specific_user(chat_id, "No such command. Type /help for help")


# Scheduling all repeating task and running initial setup.
schedule.every(5).minutes.do(check_firmware)
schedule.every(1).seconds.do(react_on_commands)
schedule.every(24).hours.do(check_version_and_notify)
set_available_commands()
schedule.run_all()  # run all tasks once at the start of the program

while True:
    schedule.run_pending()
    time.sleep(1)
