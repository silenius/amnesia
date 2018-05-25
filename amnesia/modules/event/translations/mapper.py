# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.event.translations import EventTranslation
from amnesia.modules.content.translations import ContentTranslation

def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.translations.mapper')
    config.include('amnesia.modules.event.mapper')

    orm.mapper(
        EventTranslation,
        tables['event_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'event')
    )
