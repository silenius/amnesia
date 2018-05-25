# -*- coding: utf-8 -*-

from amnesia.modules.event import Event
from amnesia.modules.event.translations import EventTranslation


def includeme(config):
    '''Pyramid includeme'''
    config.include('amnesia.modules.content.translations.config')
    config.include('.mapper')

    config.set_translatable_mapping(Event, EventTranslation)
    config.set_translatable_attrs(Event, ('body', ))
