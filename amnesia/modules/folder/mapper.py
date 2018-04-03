# -*- coding: utf-8 -*-

from sqlalchemy import orm

from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderTranslation
from amnesia.modules.content import Content
from amnesia.modules.content import ContentTranslation
from amnesia.modules.document import Document
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content_type import ContentType


def includeme(config):

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.document.mapper')

    tables = config.registry['metadata'].tables

    orm.mapper(
        FolderTranslation, tables['content_translation'],
        inherits=ContentTranslation,
        polymorphic_identity=get_type_id(config, 'folder')
    )

    orm.mapper(
        Folder, tables['folder'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'folder'),
        inherit_condition=tables['folder'].c.content_id ==
        tables['content'].c.id,
        properties={
            'alternate_index': orm.relationship(
                Document,
                primaryjoin=tables['folder'].c.index_content_id ==
                tables['document'].c.content_id,
                innerjoin=True,
                uselist=False,
                post_update=True,
                backref=orm.backref('indexes')
            ),

            'polymorphic_children': orm.relationship(
                ContentType,
                secondary=tables['folder_polymorphic_loading']
            ),
        }
    )

    dbsession = config.registry['dbsession_factory']()
    config.registry['root_folder'] = dbsession.query(Folder).filter_by(
        container_id=None).one()
    dbsession.close()


