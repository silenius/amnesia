# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Language


def includeme(config):
    tables = config.registry['metadata'].tables
    orm.mapper(Language, tables['language'])
