from sqlalchemy import orm

from amnesia.db import mapper_registry

from .model import MimeMajor
from .model import Mime

def includeme(config):
    ''' Pyramid includeme '''
    tables = config.registry['metadata'].tables

    mapper_registry.map_imperatively(
        MimeMajor,
        tables['mime_major']
    )

    mapper_registry.map_imperatively(
        Mime,
        tables['mime'],
        properties={
            'major': orm.relationship(
                MimeMajor,
                lazy='joined'
            )
        }
    )
