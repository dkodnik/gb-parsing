# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field() # *Наименование  вакансии
    salary = scrapy.Field()
    min_salary = scrapy.Field() # *Зарплата от
    max_salary = scrapy.Field() # *Зарплата до
    currency = scrapy.Field() # +валюта
    vacancy_link = scrapy.Field() # *Ссылку на саму вакансию
    _id = scrapy.Field() # +для монго
