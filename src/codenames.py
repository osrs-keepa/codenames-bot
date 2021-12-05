import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO: accept this as input
CODENAMES_URL = "https://codenames.game/room/film-drone-screen"

GameLog = []
BluePlayerLog = []
RedPlayerLog = []
GameGoing = True
CLEANR = re.compile('<.*?>')  # compile regex to remove tags once


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


def processGuessLog(l):
    # OPERATIVE GUESS FORMAT
    # name: string
    # team: 'red' | 'blue'
    # success: bool
    # word: string
    cleanGuess = cleanhtml(l.get_attribute('innerHTML'))
    name = cleanGuess.split(' ')[0]
    word = cleanGuess.split(' ')[2]
    team = 'red' if 'red' in l.get_attribute('class').split(' ')[2] else 'blue'
    success = team in l.get_attribute('class').split(' ')[3]
    return {
        'team': team,
        'name': name,
        'word': word,
        'success': success
    }


def getLogEntries(driver):
    while(True):
        try:
            GameLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//section[@class='scrollTarget flex-auto landscape:rounded-b-xl']/article"))  # xpath to cards
            )
            print('gamelog:')
            for l in GameLog:
                # check which type of log it is
                log = processGuessLog(l)
                print(log)
        except Exception:
            print('couldnt find gamelog')
        try:
            # TODO: separate operatives from spymaster
            BluePlayerLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//main[@id='teamBoard-blue']/div/div/div/section"))  # xpath to blue operatives
            )
            print('blue players:')
            for b in BluePlayerLog:
                print(b.get_attribute('innerHTML'))
        except Exception:
            print('couldnt find blue team members')
        try:
            # TODO: separate operatives from spymaster
            RedPlayerLog = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//main[@id='teamBoard-red']/div/div/div/section"))  # xpath to red operatives
            )
            print('red players:')
            for r in RedPlayerLog:
                print(r.get_attribute('innerHTML'))
        except Exception:
            print('couldnt find red team members')
        time.sleep(2)


driver = webdriver.Chrome()
driver.implicitly_wait(5)  # seconds
driver.get(CODENAMES_URL)
time.sleep(3)
print(driver.current_url)

# set nickname
login(driver)

# gotta sleep everywhere to account for loading screens
time.sleep(5)

# get a list of the cards on the board
cardList = getCards(driver)

for card in cardList:
    print(card.get_attribute('innerHTML'))

getLogEntries(driver)

# driver.close()
