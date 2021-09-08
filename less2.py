"""
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия. 
### По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение). Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas.
"""

from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd

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
            salary_min = int(salary[0]+salary[1])
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
    
    df = pd.DataFrame(vacancy_date)

    return df

vacancy = 'Python'
df = parser_vacancy(vacancy)
# Сброс ограничений на число столбцов
pd.set_option('display.max_columns', None)
print(df.head())
print(df.tail())