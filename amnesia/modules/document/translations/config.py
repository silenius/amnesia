# -*- coding: utf-8 -*-

from amnesia.modules.document import Document
from amnesia.modules.document.translations import DocumentTranslation


def includeme(config):
    config.include('amnesia.modules.content.translations.config')

    config.set_translatable_mapping(Document, DocumentTranslation)
    config.set_translatable_attrs(Document, ('body', ))
