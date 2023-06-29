import logging

from sqlalchemy import orm
from sqlalchemy import event
from sqlalchemy.types import Integer

from amnesia.db import mapper_registry
from amnesia.db.ext import pg_json_property
from amnesia.modules.folder import Folder
from amnesia.modules.content import Content
from amnesia.modules.document import Document
from amnesia.modules.content_type.utils import get_type_id
from amnesia.modules.content_type import ContentType

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)

    config.include('amnesia.modules.content.mapper')
    config.include('amnesia.modules.content_type.mapper')
    config.include('amnesia.modules.document.mapper')

    tables = config.registry['metadata'].tables

    t_folder = tables['folder']

#    q_count_children = sql.select([
#        sql.func.count('*').label('cpt')
#    ]).where(
#        t_content.c.container_id == t_folder.c.content_id
#    ).lateral('children')

    mapper_registry.map_imperatively(
        Folder,
        t_folder,
        inherits=Content,
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

#@event.listens_for(Folder, 'mapper_configured')
#def add_json_props(mapper, class_):
#    class_.default_limit = pg_json_property(
#        'props', 'default_limit', Integer, default=50
#    )
#
#@subscriber(ApplicationCreated)
#def configure_root_folder(event):
#    registry = event.app.registry
#
#    dbsession = registry['dbsession_factory']()
#
#    stmt = sql.select(Folder).options(
#        orm.lazyload('*')
#    ).where(
#        Folder.container_id == None
#    )
#
#    registry['root_folder'] = dbsession.execute(stmt).scalar_one()
#
#    dbsession.close()
