# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.tag import Tag
from amnesia.modules.content import Content


def includeme(config):
    tables = config.registry['metadata'].tables

    orm.mapper(
        Tag, tables['public.tag'], properties={
            'contents': orm.relationship(
                Content, secondary=tables['public.content_tag'],
                back_populates='tags'
            )
        }
    )
