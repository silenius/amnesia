from sqlalchemy import orm

from .model import ContentType


def includeme(config):
    tables = config.registry['metadata'].tables
    orm.mapper(ContentType, tables['content_type'])
