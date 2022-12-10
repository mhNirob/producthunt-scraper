import scrapy
from scrapy.http import Response, Request
import json
import urllib.request as urllib2
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import os
import hashlib


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['help.letsdeel.com',
                       'getshogun.com',
                       'backpack.zendesk.com',
                       'groww.in',
                       'support.cointracker.io',
                       'papa.com',
                       'vendr.net',
                       'help.observe.ai',
                       'substack.com',
                       'mutiny.com',
                       'delphia.com',
                       'help.torch.io',
                       'nuvocargo.com',
                       'gainful.com',
                       'berbix.com',
                       'alphavantage.co',
                       'pagerduty.com',
                       'help.doordash.com',
                       'help.amplitude.com',
                       'airbnb.com',
                       'university.webflow.com',
                       'help.zapier.com',
                       'fivetran.com'
                       ]
    start_urls = [
        'https://help.delphia.com/en/',
        'https://help.torch.io/',
        'https://www.nuvocargo.com/en/content/faq',
        'https://help.gainful.com/hc/en-us',
        'https://docs.berbix.com/docs/overview',
        'https://www.alphavantage.co/support/',
        'https://www.pagerduty.com/support/',
        'https://help.doordash.com/s/?language=en_US',
        'https://help.amplitude.com/hc/en-us',
        'https://www.airbnb.com/help/?audience=guest',
        'https://university.webflow.com/support',
        'https://help.zapier.com/hc/en-us',
        'https://fivetran.com/docs/getting-started/faq'
    ]

    def parse(self, response: Response):
        folderName = urlsplit(response.url).netloc
        try:
            os.mkdir("data/"+folderName)
            yield Request(response.url, callback=self.parse_urls)
        except:
            pass

    def parse_urls(self, response: Response):
        print("url -> ", response.url)
        product_urls = response.xpath(
            "*//a/@href"
        ).getall()

        # filtered_product_urls = any(s in product_urls for s in ["help"])

        # filtered_product_urls = []

        # for url in product_urls:
        #     # yield Request(url, callback=self.parse_page)
        #     if any(s in url for s in ["help"]):
        #         filtered_product_urls.append(url)
        #         url = response.urljoin(url)
        #         yield Request(url, callback=self.parse_page)

        # for url in filtered_product_urls:
        #     # convert relative url (e.g. /products/slack)
        #     # to absolute (e.g. https://producthunt.com/products/slack)
        #     print("url --> ", url)
        #     #url = response.urljoin(url)
        #     yield Request(url, callback=self.parse_urls)

        # print("urls -> ", product_urls)
        # yield Request(url, callback=self.parse_page)
        for url in product_urls:
            # convert relative url (e.g. /products/slack)
            # to absolute (e.g. https://producthunt.com/products/slack)
            #print("url --> ", url)
            if any(s in response.urljoin(url) for s in ["help", "contact", "support", "faq", "ask", "community", "zendesk", "hc"]):
                url = response.urljoin(url)
                #print("url * --> ", url)
                yield Request(url, callback=self.parse_urls)
                yield Request(url, dont_filter=True, callback=self.parse_page)

    def parse_page(self, response: Response):
        folderName = urlsplit(response.url).netloc
        filename = response.url.split("/")[-1] + '.json'

        soup = BeautifulSoup(response.body)
        title = soup.title.string

        # get text
        content = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in content.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        # drop blank lines
        content = '\n'.join(chunk for chunk in chunks if chunk)

        pageContent = {"url": str(response.url),
                       "title": title,
                       "htmlBody": str(response.body),
                       "content": content}
        json_object = json.dumps(pageContent, indent=4)

        try:
            with open("data" + "/" + folderName + "/" + hashlib.md5(str(response.url).encode('utf-8')).hexdigest()+'.json', 'w+') as file:
                file.write(json_object)
        except:
            print("File already exists!")
            pass

        # yield {
        #     'title': response.xpath('//h1/text()').get(),
        #     'subtitle': response.xpath('//h1/following-sibling::div//text()').get(),
        #     'votes': response.xpath("//*[contains(.//text(),'upvotes')]/preceding-sibling::*//text()").get(),
        #     'reviews': response.xpath("//*[contains(text(),'reviews')]/preceding-sibling::*/text() ").get(),
        # }
