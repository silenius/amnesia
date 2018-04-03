# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Document
from .model import DocumentTranslation
from ..content import Content
from ..content import ContentTranslation
from ..content_type.utils import get_type_id


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')

    orm.mapper(
        DocumentTranslation, tables['document_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'document'),
        polymorphic_load='inline'
    )

    orm.mapper(
        Document, tables['document'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'document'),
    )
