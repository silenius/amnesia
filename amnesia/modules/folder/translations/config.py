# -*- coding: utf-8 -*-

from amnesia.modules.folder import Folder
from amnesia.modules.folder.translations import FolderTranslation


def includeme(config):
    config.include('amnesia.modules.content.translations.config')
    config.include('.mapper')

    config.set_translatable_mapping(Folder, FolderTranslation)
    config.set_translatable_attrs(Folder, ('title', 'description'))
