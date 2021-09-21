import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LmruSpider(scrapy.Spider):
    name = 'lmru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super(LmruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//a[@data-qa="product-name"]')
        for link in links:
            yield response.follow(link, callback=self.parse_link)

        # next_page = response.css("a.s15wh9uj_plp::attr('href')").extract_first()
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_link(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        # loader.add_css('name', 'h1::text')
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('photos', '//img[contains(@slot, "thumbs")]/@src')
        loader.add_value('url', response.url)
        #loader.add_xpath('price', '//meta[@itemprop="price"]/@content')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('def_list', '//dt[@class="def-list__term"]/text()|//dd[@class="def-list__definition"]/text()')

        yield loader.load_item()
