# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Event
from ..content import Content
from ..content_type import ContentType
from ..content_type.utils import get_type_id
from ..country import Country


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.country.mapper')

    orm.mapper(Event, tables['event'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'event'),
        properties={
            'country': orm.relationship(Country, lazy='joined')
        })
