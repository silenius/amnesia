# -*- coding: utf-8 -*-

import json

from array import array
from datetime import datetime

from sqlalchemy import orm, sql, schema, types, event as sa_event

from amnesia import db
from amnesia.models.auth import Human
from amnesia.models.content_type import ContentType
from amnesia.models.content import Content
from amnesia.models.country import Country
from amnesia.models.event import Event
from amnesia.models.file import File
from amnesia.models.folder import Folder
from amnesia.models.mime import Mime, MimeMajor
from amnesia.models.news import News
from amnesia.models.page import Page
from amnesia.models.state import State
from amnesia.models.tag import Tag

__all__ = ['Human', 'ContentType', 'Content', 'Country', 'Event', 'File',
           'Folder', 'Mime', 'MimeMajor', 'News', 'Page', 'State', 'Tag']

#############
# LISTENERS #
#############

def update_updated_listener(mapper, connection, target):
    """ When an object is modified adjust the Content.updated column """

    target.updated = datetime.now()

def update_FTS_listener(mapper, connection, target):
    """ Set the 'fts' column (full text search) """

    weights = array('c', ('a', 'b', 'c', 'd'))
    default_weight = 'd'
    fts = None

    if target.is_fts:
        # Check which columns should be indexed
        for i in getattr(target.__class__, '__FTS__', ()):
            (field, weight) = i

            if weight.lower() not in weights:
                weight = default_weight

            _fts = sql.func.coalesce(getattr(target, field, ''), '')
            _fts = sql.func.to_tsvector(_fts)
            _fts = sql.func.setweight(_fts, weight)

            fts = _fts if fts is None else fts.op('||')(_fts)

    target.fts = fts

##########
# MODELS #
##########

class JSONEncodedDict(types.TypeDecorator):

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value is not None else None


def init_models(*args, **kwargs):

    table = db.meta.tables

    schema.Table('folder', db.meta,
        schema.Column('default_order', JSONEncodedDict()),
        autoload=True,
        extend_existing=True,
        autoload_replace=True,
        autoload_with=db.engine)

    def _get_type_id(name):
        """ This function returns the content_type ID for a given name """

        t = table['content_type']

        q = sql.select([t.c.id]).where(t.c.name == name)

        content_type_id = db.Session.execute(q).scalar()

        if not content_type_id:
            raise ValueError('Missing content type : %s' % name)

        return content_type_id

    ###########
    # MAPPERS #
    ###########

    orm.mapper(ContentType, table['content_type'])

    orm.mapper(Country, table['country'])

    orm.mapper(State, table['state'])

    orm.mapper(Tag, table['tag'])

    orm.mapper(Human, table['human'], 
        properties = {
            'count_content' : orm.column_property(
                sql.select(
                    [sql.func.count()],
                    table['human'].c.id == table['content'].c.owner_id
                ).label('count_content'),
                deferred = True
            )
        })

    orm.mapper(MimeMajor, table['mime_major'])

    orm.mapper(Mime, table['mime'],
        properties = {
            'major' : orm.relationship(MimeMajor, lazy = 'joined')
        })

    # Joined table inheritance is used.
    _count_alias = table['content'].alias('_count_children')
    orm.mapper(Content, table['content'],
        polymorphic_on = table['content'].c.content_type_id,
        properties = {

            'fts' : orm.deferred(table['content'].c.fts),

            #################
            # RELATIONSHIPS #
            #################

            'owner' : orm.relationship(
                Human,
                lazy = 'joined',
                innerjoin = True,
                backref = orm.backref('contents', lazy = 'dynamic',
                                      cascade='all, delete-orphan')
            ),

            'state' : orm.relationship(
                State,
                lazy = 'joined',
                innerjoin = True
            ),

            'type' : orm.relationship(
                ContentType, 
                lazy = 'joined',
                innerjoin = True
            ),

            'polymorphic_children' : orm.relationship(
                ContentType,
                secondary = table['content_polymorphic_loading']
            ),

            'tags' : orm.relationship(
                Tag,
                secondary = table['content_tag']
            ),

            'parent' : orm.relationship(
                Folder,
                foreign_keys = table['content'].c.container_id,
                innerjoin = True,
                uselist = False,
                backref = orm.backref('children', cascade='all, delete-orphan')
            ),

            'icon' : orm.relationship(
                File,
                # FIXME: fails with 0.8
                #lazy = 'joined',
                foreign_keys = table['content'].c.icon_content_id,
                uselist = False,
                backref = orm.backref('contents')
            ),

            #####################
            # COLUMN PROPERTIES #
            #####################

            'last_update' : orm.column_property(
                sql.func.coalesce(table['content'].c.updated,
                                  table['content'].c.added)
            ),

            'count_children' : orm.column_property(
                sql.select([sql.func.count()]).where(
                    _count_alias.c.container_id == table['content'].c.id
                ).correlate(table['content']).label('count_children'),
                deferred = True
            ),

            'row_number' : orm.column_property(
                sql.func.row_number().\
                over(partition_by=table['content'].c.container_id,
                     order_by=table['content'].c.weight.desc()),
                deferred = True
            )
        })

    orm.mapper(File, table['data'], inherits = Content,
        polymorphic_identity = _get_type_id('file'),
        inherit_condition = table['data'].c.content_id ==\
                            table['content'].c.id,
        properties = {
            'mime' : orm.relationship(
                Mime,
                lazy = 'joined'
            )
        })

    orm.mapper(Event, table['event'], inherits = Content,
        polymorphic_identity = _get_type_id('event'),
        properties = {
            'country' : orm.relationship(Country, lazy = 'joined')
        })

    orm.mapper(Folder, table['folder'], inherits = Content,
        polymorphic_identity = _get_type_id('folder'),
        inherit_condition = table['folder'].c.content_id ==\
                            table['content'].c.id,
        properties = {
            'alternate_index' : orm.relationship(
                Content,
                primaryjoin = table['folder'].c.index_content_id == \
                              table['content'].c.id,
                innerjoin = True,
                uselist = False,
                backref = orm.backref('indexes')
            )
        }
    )

    orm.mapper(Page, table['page'], inherits = Content,
        polymorphic_identity = _get_type_id('page'))

    orm.mapper(News, table['news'], inherits = Content,
        polymorphic_identity = _get_type_id('news'))

    ###################
    # EVENT LISTENERS #
    ###################

    sa_event.listen(Content, 'before_insert', update_FTS_listener,
                    propagate=True)

    sa_event.listen(Content, 'before_update', update_FTS_listener,
                    propagate=True)

    sa_event.listen(Content, 'before_update', update_updated_listener,
                    propagate=True)

    ###################
    # FULLTEXT SEARCH #
    ###################

    Content.__FTS__ =  [('title', 'A'), ('description', 'B')]
    News.__FTS__ = [('title', 'A'), ('description', 'B'), ('body', 'C')]
    Page.__FTS__ = [('title', 'A'), ('description', 'B'), ('body', 'C')]
    Event.__FTS__ = [('title', 'A'), ('description', 'B'), ('location', 'B'),
                     ('address', 'B'), ('body', 'C')]

    ####################
    # ALLOWED ORDERING #
    ####################

    Content.__order__ = [Content.weight, Content.last_update]
    Event.__order__ = [Event.starts, Event.ends]
