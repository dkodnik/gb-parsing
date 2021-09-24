"""
Написать программу, которая собирает входящие письма из своего или тестового почтового ящика и сложить данные о письмах
в базу данных (от кого, дата отправки, тема письма, текст письма полный)
Логин тестового ящика: study.ai_172@mail.ru
Пароль тестового ящика: NextPassword172???
"""

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from selenium.common import exceptions

# Монго:
db_name = 'mail_db'
client = MongoClient('localhost', 27017)
db = client[db_name]
collection = db.mail_collection

# Драйвер (Microsoft Edge - Версия 93.0.961.52 (Официальная сборка) (64-разрядная версия)):
driver = webdriver.Edge()
driver.get('https://mail.ru/')

# Авторизация:
elem = driver.find_element_by_name('login')
elem.send_keys('study.ai_172@mail.ru')
elem.send_keys(Keys.ENTER)
time.sleep(2)
elem = driver.find_element_by_name('password')
elem.send_keys('NextPassword172???')
elem.send_keys(Keys.ENTER)

first_messege = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "llc")))
first_messege.click()

while True:
    try:
        mail = {}

        time.sleep(3)

        title = driver.find_element_by_tag_name('h2').text
        letter_contact = driver.find_element_by_xpath('//span[@class="letter-contact"]').get_attribute('title')
        letter_date = driver.find_element_by_xpath('//div[@class ="letter__date"]').text

        mail['contact'] = letter_contact
        mail['date'] = letter_date
        mail['title'] = title

        try:
            letter_body = driver.find_element_by_xpath('//div[contains(@id, "BODY")]').text
            mail['body'] = letter_body
        except BaseException:
            pass

        collection.update(mail, mail, upsert=True)

        button_next = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'portal-menu-element_next')))

        ends = button_next.find_element_by_xpath('//span[contains(@class, "button2_arrow-down")]')
        try:
            is_ends = ends.get_attribute('disabled')
            if is_ends:
                print('Больше нет писем')
                break
        except BaseException:
            pass

        # ... это ещё не конец!
        button_next.click()
    except exceptions.TimeoutException:
        print('Больше нет писем 1')
        break

driver.quit()
