# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import File
from ..content import Content
from ..content_type.utils import get_type_id
from ..content_type import ContentType


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')

    orm.mapper(File, tables['data'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'file'),
        inherit_condition=tables['data'].c.content_id ==
               tables['content'].c.id
    )

