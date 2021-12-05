import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver):
    try:
        nickname_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nickname-input"))
        )
        nickname_input.clear()
        nickname_input.send_keys("codenames_bot")

        join_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//section[@class='text-center px-2']/button"))
        )
        join_button.click()
    except NoSuchElementException:
        print('couldnt find nickname-input')
        driver.quit()


def getCards(driver):
    try:
        elements = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//section[@class='absolute inline-flex justify-center items-center uppercase select-text font-lorimer landscape:font-futuraBold']/div"))
        )
        for el in elements:
            print(el.get_attribute('innerHTML'))
    except NoSuchElementException:
        print('couldnt find gamescene')
        driver.quit()


codenames_url = "https://codenames.game/room/mammoth-battery-saturn"


# i put this driver in nodejs folder for now
driver = webdriver.Chrome()
driver.implicitly_wait(5)  # seconds
driver.get(codenames_url)
time.sleep(5)
print(driver.current_url)
wait = WebDriverWait(driver, 20)

login(driver)

time.sleep(5)

getCards(driver)

print('we got it')
driver.close()
