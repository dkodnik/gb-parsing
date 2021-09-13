"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from pymongo import MongoClient
import json

from pprint import pprint

def _parser_hh(vacancy):

    vacancy_date = []
    
    params = {
        'text': vacancy, \
        'search_field': 'name', \
        'items_on_page': '100', \
        'page': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
    }

    link = 'https://hh.ru/search/vacancy'
       
    html = requests.get(link, params=params, headers=headers)
    
    if html.ok:
        parsed_html = bs(html.text,'html.parser')
        
        page_block = parsed_html.find('div', {'data-qa': 'pager-block'})
        if not page_block:
            last_page = 1
        else:
            last_page = int(page_block.find_all('span', {'class': 'pager-item-not-in-short-range'})[-1].find('span').getText())
            # не будем всё перебирать, долго ждать
            if last_page > 5:
                last_page = 5
    
    for page in range(0, last_page):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)
        
        if html.ok:
            parsed_html = bs(html.text,'html.parser')
            
            vacancy_items = parsed_html.find('div', {'data-qa': 'vacancy-serp__results'}) \
                                        .find_all('div', {'class': 'vacancy-serp-item'})
                
            for item in vacancy_items:
                vacancy_date.append(_parser_item_hh(item))
                
    return vacancy_date

def _parser_item_hh(item):

    vacancy_date = {}
    
    # vacancy_name
    vacancy_name = item.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).getText() \
                        .replace(u'\xa0', u' ')
    
    vacancy_date['vacancy_name'] = vacancy_name
    
    # company_name
    company_name = item.find('div', {'class': 'vacancy-serp-item__meta-info'}) \
                        .find('a') \
                        .getText()
    
    vacancy_date['company_name'] = company_name
    
    # city
    city = item.find('span', {'class': 'vacancy-serp-item__meta-info'}) \
                .getText() \
                .split(', ')[0]
    
    vacancy_date['city'] = city
    
    #metro station
    metro_station = item.find('span', {'class': 'vacancy-serp-item__meta-info'}).findChild()

    if not metro_station:
        metro_station = None
    else:
        metro_station = metro_station.getText()
        
    vacancy_date['metro_station'] = metro_station
    
    #salary
    salary = item.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary = salary.getText() \
                        .replace(u'\xa0', u'')

        salary = re.split(r'\s|-', salary)
        
        if salary[0] == 'до':
            salary_min = None
            salary_max = int("".join(salary[1:-1]))
        elif salary[0] == 'от':
            salary_min = int("".join(salary[1:-1]))
            salary_max = None
        else:
            #print(salary)
            if salary[1] != '–':
                salary_min = int(salary[0]+salary[1])
            else:
                salary_min = int(salary[0])
            salary_max = int(salary[-3]+salary[-2])
        
        salary_currency = salary[-1]
        
    vacancy_date['salary_min'] = salary_min
    vacancy_date['salary_max'] = salary_max
    vacancy_date['salary_currency'] = salary_currency
    
    # link
    vacancy_date['vacancy_link'] = item.find('span', {'class': 'resume-search-item__name'}).find('a')['href']
    
    # site
    vacancy_date['site'] = 'hh.ru'
    
    return vacancy_date

def _parser_superjob(vacancy):
    vacancy_date = []
    
    params = {
        'keywords': vacancy, \
        'profession_only': '1', \
        'geo[c][0]': '15', \
        'geo[c][1]': '1', \
        'geo[c][2]': '9', \
        'page': ''
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'
    }
    
    link = 'https://www.superjob.ru/vacancy/search/'
       
    html = requests.get(link, params=params, headers=headers)
    
    if html.ok:
        parsed_html = bs(html.text,'html.parser')
    
        page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        last_page = 1
    else:
        page_block = page_block.findParent()
        last_page = int(page_block.find_all('a')[-2].getText())
    
    for page in range(0, last_page + 1):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)
        
        if html.ok:
            parsed_html = bs(html.text,'html.parser')
            vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})
                        
            for item in vacancy_items:
                vacancy_date.append(_parser_item_superjob(item))
                
    return vacancy_date

def _parser_item_superjob(item):

    vacancy_date = {}
    
    # vacancy_name
    vacancy_name = item.find_all('a')
    if len(vacancy_name) > 1:
        vacancy_name = vacancy_name[-2].getText()
    else:
        vacancy_name = vacancy_name[0].getText()
    vacancy_date['vacancy_name'] = vacancy_name
    
    # company_name
    company_name = item.find('span', {'class': 'f-test-text-vacancy-item-company-name'})
    
    if not company_name:
        company_name = item.findParent() \
                            .find('span', {'class': 'f-test-text-vacancy-item-company-name'}) \
                            .getText()
    else:
        company_name = company_name.getText()
    
    vacancy_date['company_name'] = company_name
    
    # city
    company_location = item.find('span', {'class': 'f-test-text-company-item-location'}) \
                            .findChildren()[1] \
                            .getText() \
                            .split(',')
    
    vacancy_date['city'] = company_location[0]
    
    #metro station
    if len(company_location) > 1:
        metro_station = company_location[1]
    else:
        metro_station = None
    
    vacancy_date['metro_station'] = metro_station
    
    #salary
    salary = item.find('span', {'class': 'f-test-text-company-item-salary'}) \
                  .findChildren()
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary_currency = salary[-1].getText()
        is_check_sarary = item.find('span', {'class': 'f-test-text-company-item-salary'}) \
                                .getText() \
                                .replace(u'\xa0', u' ') \
                                .split(' ', 1)[0]
        if is_check_sarary == 'до' or len(salary) == 2:
            salary_min = None
            salary_max = int(salary[0].getText() \
                                        .replace(u'\xa0', u'').replace(u'до', u'') \
                .replace(u'руб.', u''))
        elif is_check_sarary == 'от':
            salary_min = int(salary[0].getText() \
                .replace(u'\xa0', u'') \
                .replace(u'от', u'') \
                .replace(u'руб.', u''))
            salary_max = None
        elif salary[0].getText() == 'По договорённости':
            salary_min = None
            salary_max = None
        elif salary[0].getText().find('—')!=-1:
            salary_arr = salary[0].getText().split('—')
            salary_min = int(salary_arr[0].replace(u'\xa0', u'').replace(u'руб.', u''))
            salary_max = int(salary_arr[1].replace(u'\xa0', u'').replace(u'руб.', u''))
        else:
            salary_min = int(salary[0].getText() \
                                         .replace(u'\xa0', u'').replace(u'от', u'') \
                .replace(u'руб.', u''))
            try:
                salary_max = int(salary[2].getText() \
                                         .replace(u'\xa0', u'').replace(u'до', u'') \
                .replace(u'руб.', u''))
            except Exception:
                salary_max = None
        
    vacancy_date['salary_min'] = salary_min
    vacancy_date['salary_max'] = salary_max
    vacancy_date['salary_currency'] = salary_currency
    
    
    # link
    vacancy_link = item.find_all('a')
    
    if len(vacancy_link) > 1:
        vacancy_link = vacancy_link[-2]['href']
    else:
        vacancy_link = vacancy_link[0]['href']
    
    vacancy_date['vacancy_link'] = f'https://www.superjob.ru{vacancy_link }'
    
    # site
    vacancy_date['site'] = 'www.superjob.ru'
    
    return vacancy_date

def parser_vacancy(vacancy):
        
    vacancy_date = []
    vacancy_date.extend(_parser_hh(vacancy))
    vacancy_date.extend(_parser_superjob(vacancy))

    return vacancy_date

def connect_db(mongodb_uri, db_name, collection_name):
    mongodb = MongoClient(mongodb_uri)
    db = mongodb[db_name]
    collection = db[collection_name]
    return collection

def add_one(collection, d1):
    collection.insert_one(d1)

def upd_one(collection, d1):
    collection.update_one({'vacancy_link': d1['vacancy_link']}, {'$set': d1})

# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД.
def add_all(collection, vac_data):
    #collection.insert_many(df)
    add_amnt = 0
    upd_amnt = 0
    for d1 in vac_data:
        if is_exists(collection, 'vacancy_link', d1['vacancy_link']):
            upd_one(collection, d1)
            upd_amnt += 1
        else:
            add_one(collection, d1)
            add_amnt += 1
    print(f"Add: {add_amnt}\nUpd: {upd_amnt}\n")

# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
def print_salary_max(collection, salary):
    objects = collection.find({'salary_max': {'$gt': salary}})
    for obj in objects:
        pprint(obj)

# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
def is_exists(collection, name_tags, field):
    return bool(collection.find_one({name_tags: {"$in": [field]}}))

coll = connect_db('mongodb://localhost:27017/', 'vacancy', 'vacancy_db')


vacancy = 'Python'
vac_data = parser_vacancy(vacancy)
print("Ammount:", len(vac_data))

add_all(coll, vac_data)

print_salary_max(coll, 300000)