# -*- coding: utf-8 -*-

from pyramid.events import subscriber
from pyramid.events import ApplicationCreated

from sqlalchemy import orm

from amnesia.modules.folder import Folder
from amnesia.modules.content import Content
from amnesia.modules.document import Document
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content_type import ContentType


def includeme(config):
    config.scan(__name__)

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.document.mapper')

    tables = config.registry['metadata'].tables

    orm.mapper(
        Folder, tables['folder'], inherits=Content,
        polymorphic_identity=get_type_id(config, 'folder'),
        inherit_condition=tables['folder'].c.content_id ==
        tables['content'].c.id,
        properties={
            'alternate_index': orm.relationship(
                lambda: Document,
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


@subscriber(ApplicationCreated)
def configure_root_folder(event):
    registry = event.app.registry

    dbsession = registry['dbsession_factory']()

    registry['root_folder'] = dbsession.query(Folder).options(
        orm.noload('*')
    ).filter_by(
        container_id=None
    ).one()

    dbsession.close()
