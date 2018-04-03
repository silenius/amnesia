# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.mime import Mime
from amnesia.modules.file import File
from amnesia.modules.file import FileTranslation
from amnesia.modules.content import Content
from amnesia.modules.content import ContentTranslation

from amnesia.modules.content_type.utils import get_type_id


def includeme(config):
    ''' Pyramid includeme '''
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.mime.mapper')

    orm.mapper(
        FileTranslation, tables['content_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'file')
    )

    orm.mapper(
        File, tables['data'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'file'),
        properties={
            'mime': orm.relationship(Mime, lazy='joined')
        }
    )
