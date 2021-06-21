# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.db import mapper_registry

from .model import Language


def includeme(config):
    tables = config.registry['metadata'].tables

    mapper_registry.map_imperatively(
        Language, tables['language']
    )
