# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.event import Event
from amnesia.modules.content import Content
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.country import Country


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.country.mapper')

    orm.mapper(
        Event, tables['event'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'event'),
        properties={
            'country': orm.relationship(
                Country, lazy='joined'
            ),
        }
    )
