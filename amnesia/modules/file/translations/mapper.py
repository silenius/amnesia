
# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content.translations import ContentTranslation
from amnesia.modules.file.translations import FileTranslation


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.translations.mapper')
    config.include('amnesia.modules.file.mapper')

    orm.mapper(
        FileTranslation,
        tables['content_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'file')
    )
