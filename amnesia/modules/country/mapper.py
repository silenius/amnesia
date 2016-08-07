from sqlalchemy import orm

from .model import Country


def includeme(config):
    tables = config.registry['metadata'].tables
    orm.mapper(Country, tables['country'])
