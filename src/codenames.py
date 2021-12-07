import time
import re
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO: accept this as input
CODENAMES_URL = "https://codenames.game/room/train-steam-rodeo"

REFRESH_RATE = 5
CLEANR = re.compile('<.*?>')  # compile regex to remove tags once

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('codenames_bot')
fh = logging.FileHandler('gamelogs.log')
logger.addHandler(fh)


def login(driver):
    # joins the game with nickname 'codenames_bot'
    try:
        nickname_input = WebDriverWait(driver, 10).until(
            # nickname button when you load in
            EC.presence_of_element_located((By.ID, "nickname-input"))
        )
        nickname_input.clear()
        nickname_input.send_keys("codenames_bot")

        join_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                # "Join the Room" button
                (By.XPATH, "//section[@class='text-center px-2']/button"))
        )
        join_button.click()
    except Exception:
        print('couldnt find nickname-input')
        driver.quit()


def getCards(driver):
    # get the list of cards, not sure what we are going to do with this
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//section[@class='absolute inline-flex justify-center items-center uppercase select-text font-lorimer landscape:font-futuraBold']/div"))  # xpath to cards
        )
        return elements
    except Exception:
        print('couldnt find gamescene')
        driver.quit()


def cleanhtml(raw_html):
    # removes the <b> <em> tags from our log
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def processClueLog(l):
    # SPYMASTER CLUE FORMAT
    # name: string
    # team: 'red' | 'blue'
    # word: string
    cleanGuess = cleanhtml(l.get_attribute('innerHTML'))
    name = cleanGuess.split(' gives clue ')[0]
    # logger cant handle the infinity symbol
    word = cleanGuess.split(' gives clue ')[1].replace('\u221e', 'infinity')
    team = 'red' if 'red' in l.get_attribute('class').split(' ')[3] else 'blue'
    return {
        'team': team,
        'name': name,
        'word': word
    }


def processGuessLog(l):
    # OPERATIVE GUESS FORMAT
    # name: string
    # team: 'red' | 'blue'
    # success: bool
    # word: string
    cleanGuess = cleanhtml(l.get_attribute('innerHTML'))
    name = cleanGuess.split(' taps ')[0]
    word = cleanGuess.split(' taps ')[1]
    team = 'red' if 'red' in l.get_attribute('class').split(' ')[2] else 'blue'
    success = team in l.get_attribute('class').split(' ')[3]
    return {
        'team': team,
        'name': name,
        'word': word,
        'success': success
    }


def dumpLogs(gameLogs, bluePlayerLogs, redPlayerLogs):
    bluePlayers = list(
        map(lambda b: b.get_attribute('innerHTML'), bluePlayerLogs))
    redPlayers = list(
        map(lambda r: r.get_attribute('innerHTML'), redPlayerLogs))
    logger.info('-------------------- GAME LOGS ----------------------')
    logger.info('BLUE PLAYERS: %s', bluePlayers)
    logger.info('RED PLAYERS: %s', redPlayers)
    logger.info('RED SPYMASTER (maybe): %s', redPlayers[-1])
    logger.info('BLUE SPYMASTER (maybe): %s', bluePlayers[-1])
    for l in gameLogs:
        if "taps" in l.get_attribute('innerHTML'):
            logger.info(processGuessLog(l))
        elif "gives clue" in l.get_attribute('innerHTML'):
            logger.info(processClueLog(l))


def getLogEntries(driver):
    RedPlayerLog = []
    BluePlayerLog = []
    GameLog = []
    while(True):
        try:
            GameLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//section[@class='scrollTarget flex-auto landscape:rounded-b-xl']/article"))  # xpath to cards
            )
        except Exception as err:
            print('couldnt find gamelog:', err)
        try:
            # TODO: separate operatives from spymaster
            # for now just going to assume the last player on the list is the spy
            BluePlayerLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//main[@id='teamBoard-blue']/div/div/div/section"))  # xpath to blue operatives
            )
        except Exception:
            print('couldnt find blue team members')
        try:
            # TODO: separate operatives from spymaster
            # for now just going to assume the last player on the list is the spy
            RedPlayerLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//main[@id='teamBoard-red']/div/div/div/section"))  # xpath to red operatives
            )
        except Exception:
            print('couldnt find red team members')
        if(True in ("team wins" in l.get_attribute('innerHTML').lower() for l in GameLog)):
            print('game ended')
            dumpLogs(GameLog, BluePlayerLog, RedPlayerLog)
        dumpLogs(GameLog, BluePlayerLog, RedPlayerLog)
        time.sleep(30)


driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.get(CODENAMES_URL)
time.sleep(3)

# set nickname
login(driver)

# sleep to account for loading screens
time.sleep(5)

# get a list of the cards on the board
cardList = getCards(driver)

for card in cardList:
    print(card.get_attribute('innerHTML'))

getLogEntries(driver)
