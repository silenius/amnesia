from sqlalchemy import orm

from .model import State


def includeme(config):
    tables = config.registry['metadata'].tables
    orm.mapper(State, tables['public.state'])
