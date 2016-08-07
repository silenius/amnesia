from sqlalchemy import orm

from .model import Tag


def includeme(config):
    tables = config.registry['metadata'].tables
    orm.mapper(Tag, tables['tag'])
