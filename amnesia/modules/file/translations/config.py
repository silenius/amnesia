# -*- coding: utf-8 -*-

from amnesia.modules.file import File
from amnesia.modules.file.translations import FileTranslation


def includeme(config):
    config.include('amnesia.modules.content.translations.config')
    config.include('.mapper')

    config.set_translatable_mapping(File, FileTranslation)
