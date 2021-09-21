from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings
from leroymerlin.spiders.lmru import LmruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # search_list = ['картины', 'люстры', 'смеситель для кухни']
    search_list = ['смеситель для кухни']

    for item in search_list:
        process.crawl(LmruSpider, query=item)

    process.start()
