# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.db import mapper

from amnesia.modules.tag import Tag
from amnesia.modules.content import Content


def includeme(config):
    tables = config.registry['metadata'].tables

    mapper_registry.map_imperatively(
        Tag,
        tables['tag'],
        properties={
            'contents': orm.relationship(
                Content,
                secondary=tables['content_tag'],
                back_populates='tags'
            )
        }
    )
