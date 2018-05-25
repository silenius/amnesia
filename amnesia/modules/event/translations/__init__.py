# -*- coding: utf-8 -*-

from .model import EventTranslation


def includeme(config):
    config.include('amnesia.modules.content.translations')
    config.include('.mapper')
    config.include('.config')
