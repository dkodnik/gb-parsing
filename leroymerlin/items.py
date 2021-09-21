# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def process_url(value):
    if value:
        value = value.replace('w_82,h_82', 'w_2000,h_2000')
    return value


def process_def_list(value):
    if value:
        value = value.replace('  ', '').replace('\n', '')
    return value


class LeroymerlinItem(scrapy.Item):
    name = scrapy.Field(outpun_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_url))
    def_list = scrapy.Field(input_processor=MapCompose(process_def_list))
    _id = scrapy.Field()  # для монго
