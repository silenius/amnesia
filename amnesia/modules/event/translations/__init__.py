# -*- coding: utf-8 -*-


from .model import EventTranslation


def includeme(config):
    config.include('.mapper')
