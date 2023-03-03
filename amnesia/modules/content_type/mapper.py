from amnesia.db import mapper_registry

from .model import ContentType


def includeme(config):
    tables = config.registry['metadata'].tables

    mapper_registry.map_imperatively(
        ContentType,
        tables['content_type']
    )
