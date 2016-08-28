# -*- coding: utf-8 -*-

from sqlalchemy import orm

from .model import Folder
from ..content import Content
from ..content_type.utils import get_type_id
from ..content_type import ContentType


def includeme(config):
    tables = config.registry['metadata'].tables

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')

    orm.mapper(Folder, tables['folder'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'folder'),
        inherit_condition=tables['folder'].c.content_id ==
               tables['content'].c.id,
        properties={
            'alternate_index': orm.relationship(
                Content,
                primaryjoin=tables['folder'].c.index_content_id ==
                tables['content'].c.id,

                innerjoin=True,
                uselist=False,
                post_update=True,
                backref=orm.backref('indexes')
            ),

            'polymorphic_children': orm.relationship(
                ContentType,
                secondary=tables['folder_polymorphic_loading']
            )
        }
    )

