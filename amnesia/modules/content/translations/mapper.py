# -*- coding: utf-8 -*-

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.translations import setup_translation
from amnesia.modules.content import Content
from amnesia.modules.language import Language
from amnesia.modules.content.translations import ContentTranslation


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')

    orm.mapper(
        ContentTranslation,
        tables['content_translation'],
        # pylint: disable=no-member
        polymorphic_on=sql.select([
            Content.content_type_id
        ]).where(
            tables['content_translation'].c.content_id == Content.id
        ).correlate_except(Content).as_scalar(),
        properties={
            'language': orm.relationship(
                Language,
                lazy='joined',
                innerjoin=True,
                uselist=False
            ),

            'content': orm.relationship(
                Content,
                lazy='joined',
                innerjoin=True,
                uselist=False
            ),

        }
    )

    setup_translation(Content, ContentTranslation)
