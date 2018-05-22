# -*- coding: utf-8 -*-

from sqlalchemy import orm
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property

from amnesia.modules.event import Event
from amnesia.modules.content import Content
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.country import Country


@event.listens_for(Event, 'mapper_configured', once=True)
def add_translation_hybrid_properties(mapper, class_):

    @hybrid_property
    def body(self):
        return getattr(self.current_translation, 'body')

    @body.setter
    def body(self, value):
        setattr(self.current_translation, 'body', value)

    setattr(class_, 'body', body)


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
