# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Document
from ..content import Content
from ..content_type import ContentType
from ..content_type.utils import get_type_id


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')

    orm.mapper(Document, tables['document'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'document'))
