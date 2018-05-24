# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.document import Document
from amnesia.modules.content import Content
from amnesia.modules.content_type.utils import get_type_id


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')

    orm.mapper(
        Document, tables['document'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'document')
    )
