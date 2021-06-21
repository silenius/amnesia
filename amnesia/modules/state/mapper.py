from sqlalchemy import orm

from amnesia.db import mapper_registry

from .model import State


def includeme(config):
    tables = config.registry['metadata'].tables

    mapper_registry.map_imperatively(
        State,
        tables['state']
    )
