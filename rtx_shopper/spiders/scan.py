import scrapy
from rtx_shopper.rtx_cards import RTX_CARDS
from urllib.parse import urljoin
import logging

BASE_URL = 'http://www.scan.co.uk'
OUT_OF_STOCK = 'http://schema.org/OutOfStock'


class ScanSpider(scrapy.Spider):
    name = 'scan'
    allowed_domains = ['www.scan.co.uk']
    start_urls = [
        'http://www.scan.co.uk/shop/gaming/gpu-nvidia/nvidia-geforce-rtx-3090-graphics-cards',
        'http://www.scan.co.uk/shop/gaming/gpu-nvidia/nvidia-geforce-rtx-3080-graphics-cards',
        'http://www.scan.co.uk/shop/gaming/gpu-nvidia/nvidia-geforce-rtx-3070-graphics-cards',
        'http://www.scan.co.uk/shop/gaming/gpu-nvidia/geforce-rtx-3060-ti-graphics-cards',
        'http://www.scan.co.uk/shop/gaming/gpu-nvidia/nvidia-geforce-rtx-3060-graphics-cards',
    ]

    @staticmethod
    def get_card_from_url(url):
        matching_url = url.replace('-', '')
        for card in RTX_CARDS:
            if f'{card}ti' not in matching_url and card in matching_url:
                return f'RTX-{card}'

    def parse(self, response):
        selector = scrapy.Selector(response)
        
        self.log("GETTING URLS")
        for entry in selector.xpath("//span[@class='description']/a/@href"):
            raw_url = entry.get()
            if self.get_card_from_url(raw_url):
                yield scrapy.Request(url=urljoin(BASE_URL, raw_url))
        
        for entry in selector.xpath("//link[@itemprop='availability']/@href"):
            
            availability_schema = entry.get()
            card_name = self.get_card_from_url(response.url)
            
            if availability_schema != OUT_OF_STOCK:
                self.log(f'{card_name} IN STOCK: {response.url}', level=logging.INFO)
            elif availability_schema == OUT_OF_STOCK:
                self.log(f'{card_name} OUT OF STOCK: {response.url}', level=logging.DEBUG)
