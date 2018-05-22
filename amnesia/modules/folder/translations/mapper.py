# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.content_type.utils import get_type_id
from amnesia.translations import setup_translation
from amnesia.modules.folder import Folder
from amnesia.modules.content.translations import ContentTranslation
from amnesia.modules.folder.translations import FolderTranslation

def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.translations.mapper')
    config.include('amnesia.modules.folder.mapper')

    orm.mapper(
        FolderTranslation,
        tables['content_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'folder')
    )

    setup_translation(Folder, FolderTranslation)
