import re
import scrapy

from models import Hero, Skill

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient

engine = create_engine('postgresql://dota:dota@localhost/dota', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

client = MongoClient()
db = client.dota
heroes = db.heroes


class HeroSpider(scrapy.Spider):
    name = 'dotaspider'

    def start_requests(self):
        urls = ['http://dota.wikia.com/wiki/Defense_of_the_Ancients_Wiki']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for hero in response.xpath('//body//span[@class="character_icon"]/a/@href'):
            yield response.follow('http://dota.wikia.com' + str(hero.extract()), self.parse)
            # yield {'heroe': 'http://dota.wikia.com' + str(hero.extract())}

        names = []
        lore = ''
        for skill in response.xpath('//body//div[@title="Dota 2"]/table/tr'):
            skill_names = skill.xpath('//td[1]/b/text()')
            for name in skill_names.extract():
                if 'Ability Name' not in name and name not in names:
                    names.append(name)

        descs = response.xpath('//body//div[@title="Dota 2"]/table/tr/td[2]').extract()[1:]

        descs = [re.sub('<.*?>', '', x) for x in descs]
        self.log(descs)

        for lore_found in response.xpath('//body//div[@title="Lore"]'):
            value = lore_found.xpath('//p[2]').extract()
            lore = ' '.join(value).strip().replace('  ', '').replace('\n', '')
            if len(lore) < 20:
                value = lore_found.xpath('//p[3]').extract()
                lore = ' '.join(value).strip().replace('  ', '').replace('\n', '')
            lore = re.sub('<.*?>', '', lore)

        hero_type = response.xpath('//body//tr[contains(td, " Attributes")]').extract()[0]
        if 'Agility' in hero_type:
            hero_type = 'Agility'
        if 'Intelligence' in hero_type:
            hero_type = 'Intelligence'
        if 'Strength' in hero_type:
            hero_type = 'Strength'

        hero_name = response.url.split('/')[-1]

        hero = Hero()
        hero.lore = lore
        hero.name = hero_name
        hero.type = hero_type
        session.add(hero)
        session.commit()

        mongo_skills = []
        mongo_hero = {
            'lore': lore,
            'name': hero_name,
            'type': hero_type
        }

        i = 0
        for name in names:
            db_skill = Skill()
            db_skill.name = name
            db_skill.description = descs[i]
            db_skill.hero_id = hero.id
            session.add(db_skill)
            mongo_skills.append({
                'name': name,
                'description': descs[i],
            })
            i += 1

        mongo_hero['skills'] = mongo_skills
        heroes.insert_one(mongo_hero)

        session.commit()

        session.close()
