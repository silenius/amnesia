# -*- coding: utf-8 -*-

from .model import ContentTranslation


def includeme(config):
    config.include('.mapper')
    config.include('.config')
