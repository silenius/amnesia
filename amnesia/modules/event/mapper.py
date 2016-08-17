# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Event
from ..content import Content
from ..content_type import ContentType
from ..country import Country


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.country.mapper')

    orm.mapper(Event, tables['event'], inherits=Content,
        polymorphic_identity=3,
        properties={
            'country': orm.relationship(Country, lazy='joined')
        })
