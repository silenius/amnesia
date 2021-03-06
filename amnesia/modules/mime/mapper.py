# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import MimeMajor
from .model import Mime

def includeme(config):
    ''' Pyramid includeme '''
    tables = config.registry['metadata'].tables

    orm.mapper(
        MimeMajor, tables['mime_major']
    )

    orm.mapper(
        Mime, tables['mime'],
        properties={
            'major': orm.relationship(MimeMajor, lazy='joined')
        }
    )
