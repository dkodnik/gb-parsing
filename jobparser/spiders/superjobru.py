import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru']

    def __init__(self, vacancy=None):
        super(SuperjobruSpider, self).__init__()
        self.start_urls = [f'https://russia.superjob.ru/vacancy/search/?keywords={vacancy}']



    def parse(self, response:HtmlResponse):
        links = response.xpath("//div[contains(@class,'f-test-vacancy-item')]//a[contains(@class,'_6AfZ9')]/@href").extract()

        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)
        next_page = response.css("a.f-test-link-Dalshe::attr('href')").extract_first() #f-test-button-dalshe f-test-link-Dalshe
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        vacancy_name = response.xpath("//h1/text()").extract_first()
        #vacancy_salary = response.xpath("//span[@class='_1OuF_ ZON4b']/*/text()").extract()
        vacancy_salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").extract()

        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, vacancy_link=response.url)
