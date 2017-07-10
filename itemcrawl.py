import re
import scrapy

from models import Item

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

engine = create_engine('postgresql://dota:dota@localhost/dota', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

client = MongoClient()
db = client.dota
items = db.items


class ItemSpider(scrapy.Spider):
    name = 'itemspider'

    def start_requests(self):
        urls = ['http://dota.wikia.com/wiki/Category:Items_(DOTA2)']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for item in response.xpath('//body//div[@class="mw-content-ltr"]//li/a/@href'):
            yield response.follow('http://dota.wikia.com' + str(item.extract()), self.parse)
            # yield {'heroe': 'http://dota.wikia.com' + str(hero.extract())}

        item_name = response.url.split('/')[-1]
        item_desc = response.xpath('//body//table[@class="infobox"]//td[@colspan="2"]//i/text()').extract()[0]
        item_effect = response.xpath('//body//table[@class="infobox"]//tr[4]//td[last()]/text()').extract()[0]
        item_cost = response.xpath('//body//table[@class="infobox"]//tr[6]//td[last()]/text()').extract()[0]

        item = Item()
        item.name = item_name
        item.description = re.sub('<.*?>', '', item_desc).replace('\n', '')
        item.effects = re.sub('<.*?>', '', item_effect).replace('\n', '')
        item.cost = int(re.sub('<.*?>', '', item_cost).replace('\n', ''))

        mongo_item = {
            'name': item_name,
            'description': re.sub('<.*?>', '', item_desc).replace('\n', ''),
            'effects': re.sub('<.*?>', '', item_effect).replace('\n', ''),
            'cost': int(re.sub('<.*?>', '', item_cost).replace('\n', '')),
        }
        items.insert_one(mongo_item)

        session.add(item)
        session.commit()
        self.log(item_effect)

        session.close()
