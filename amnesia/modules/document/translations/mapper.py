# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content.translations import ContentTranslation
from amnesia.modules.document.translations import DocumentTranslation


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.translations.mapper')
    config.include('amnesia.modules.document.mapper')

    orm.mapper(
        DocumentTranslation,
        tables['document_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'document')
    )
