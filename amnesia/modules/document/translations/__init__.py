# -*- coding: utf-8 -*-


from .model import DocumentTranslation
from amnesia.modules.document import Document


def includeme(config):
    config.include('amnesia.modules.content.translations')
    config.include('.mapper')
    config.include('.config')
