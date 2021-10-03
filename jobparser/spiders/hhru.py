import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy=None):
        super(HhruSpider, self).__init__()
        self.start_urls = [f'https://hh.ru/search/vacancy?fromSearchLine=true&st=searchVacancy&text={vacancy}']

    def parse(self, response:HtmlResponse):
        links = response.xpath("//a[@data-qa ='vacancy-serp__vacancy-title']/@href").extract()
        for link in links:
            yield response.follow(link, callback = self.vacancy_parse)
        next_page = response.xpath("//a[@data-qa ='pager-next']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


    def vacancy_parse(self, response:HtmlResponse):
        vacancy_name = response.xpath("//h1//text()").extract_first()
        vacancy_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()

        yield JobparserItem(name=vacancy_name, salary=vacancy_salary, vacancy_link=response.url)
