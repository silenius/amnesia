# -*- coding: utf-8 -*-

from .model import DocumentTranslation


def includeme(config):
    config.include('amnesia.modules.content.translations')
    config.include('.mapper')
    config.include('.config')
