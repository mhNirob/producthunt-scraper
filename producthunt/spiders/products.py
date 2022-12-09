import scrapy
from scrapy.http import Response, Request


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['producthunt.com']
    start_urls = [
        'https://www.producthunt.com/topics/developer-tools',
        'https://www.producthunt.com/topics/tech',
    ]

    def parse(self, response: Response):
        product_urls = response.xpath(
            "//main[contains(@class,'layoutMain')]//a[contains(@class,'_title_')]/@href"
        ).getall()
        for url in product_urls:
            # convert relative url (e.g. /products/slack)
            # to absolute (e.g. https://producthunt.com/products/slack)
            url = response.urljoin(url)
            yield Request(url, callback=self.parse_product)
        # or shortcut in scrapy >2.0
        # yield from response.follow_all(product_urls, callback=self.parse_product)

    # def parse_product(self, response: Response):
    #     print(response)

    def parse_product(self, response: Response):

        yield {
            'title': response.xpath('//h1/text()').get(),
            'subtitle': response.xpath('//h1/following-sibling::div//text()').get(),
            'votes': response.xpath("//*[contains(.//text(),'upvotes')]/preceding-sibling::*//text()").get(),
            'reviews': response.xpath("//*[contains(text(),'reviews')]/preceding-sibling::*/text() ").get(),
        }
