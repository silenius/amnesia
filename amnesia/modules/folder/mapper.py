# -*- coding: utf-8 -*-

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia.modules.folder import Folder
from amnesia.modules.content import Content
from amnesia.modules.document import Document
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content_type import ContentType


def includeme(config):

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.document.mapper')

    tables = config.registry['metadata'].tables

    t_content = tables['content']
    t_folder = tables['folder']
    t_document = tables['document']

#    q_count_children = sql.select([
#        sql.func.count('*').label('cpt')
#    ]).where(
#        t_content.c.container_id == t_folder.c.content_id
#    ).lateral('children')

    orm.mapper(Folder, t_folder, inherits=Content,
        polymorphic_identity=get_type_id(config, 'folder'),
        inherit_condition=t_folder.c.content_id == t_content.c.id,
        properties={
            'alternate_index': orm.relationship(
                Document,
                primaryjoin=t_folder.c.index_content_id == t_document.c.content_id,
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


