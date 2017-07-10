from sqlalchemy import create_engine
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

engine = create_engine('postgresql://dota:dota@localhost/dota', echo=True)

Base = declarative_base()


class Hero(Base):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    lore = Column(String)
    created = Column(DateTime, default=datetime.now)


class Skill(Base):
    __tablename__ = 'skills'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    hero_id = Column(Integer, ForeignKey('heroes.id', ondelete='CASCADE'))
    created = Column(DateTime, default=datetime.now)


class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    effects = Column(String)
    cost = Column(Integer)
    created = Column(DateTime, default=datetime.now)


class HeroHasItem(Base):
    __tablename__ = 'heroes_items'
    id = Column(Integer, primary_key=True)
    hero_id = Column(Integer, ForeignKey('heroes.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    obtained = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)
