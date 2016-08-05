# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy import event as sa_event

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

from pytz import timezone

from .account.model import Account
from .content_type.model import ContentType
from .content.model import Content
from .country.model import Country
from .event.model import Event
from .file.model import File
from .folder.model import Folder
from .mime.model import Mime
from .mime.model import MimeMajor
from .news.model import News
from .page.model import Page
from .state.model import State
from .tag.model import Tag

from ..utils import UniqueDict

DBSession=scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
meta=MetaData()

__all__ = ['Account', 'ContentType', 'Content', 'Country', 'Event', 'File',
           'Folder', 'Mime', 'MimeMajor', 'News', 'Page', 'State', 'Tag']

orders=UniqueDict()

#############
# LISTENERS #
#############

def update_updated_listener(mapper, connection, target):
    """ When an object is modified adjust the Content.updated column """

    target.updated=datetime.now(timezone('Europe/Brussels'))

# TODO: update only if content changed.
def update_FTS_listener(mapper, connection, target):
    """ Set the 'fts' column (full text search) """

    weights=('a', 'b', 'c', 'd')
    default_weight='d'
    fts=None

    if target.is_fts:
        # Check which columns should be indexed
        for i in getattr(target.__class__, '_FTS_', ()):
            (field, weight)=i

            if weight.lower() not in weights:
                weight=default_weight

            _fts=sql.func.coalesce(getattr(target, field, ''), '')
            _fts=sql.func.to_tsvector(_fts)
            _fts=sql.func.setweight(_fts, weight)

            fts=_fts if fts is None else fts.op('||')(_fts)

    target.fts=fts

##########
# MODELS #
##########

#class JSONEncodedDict(types.TypeDecorator):
#    """ Represents an immutable structure as a JSON-encoded string. """
#
#    impl=types.TEXT
#
#    def process_bind_param(self, value, dialect):
#        return json.dumps(value) if value is not None else None
#
#    def process_result_value(self, value, dialect):
#        return json.loads(value) if value is not None else None

#class DefaultOrder(types.TypeDecorator):
#
#    impl=JSON
#
#    def process_bind_param(self, value, dialect):
#        cherrypy.log(str(value))
#        return value
#
#    def process_result_value(self, value, dialect):
#        #return [{k: orders[v] if k == 'key' else v for (k, v) in o.items()
#        #         if o['key'] in orders} for o in value] if value else None
#        if not value:
#            return None
#
#        result=[]
#
#        for d in value:
#            o=orders.get(d['key'])
#
#            if not o:
#                continue
#
#            d['obj']=o
#            result.append(d)
#
#        return result


def init_models(*args, **kwargs):

    table=meta.tables

#    schema.Table('folder', db.meta,
#        schema.Column('default_order', DefaultOrder()),
#        autoload=True,
#        extend_existing=True,
#        autoload_replace=True,
#        autoload_with=db.engine)

    def _get_type_id(name):
        """ This function returns the content_type id for a given name """

        t=table["content_type"]

        q=sql.select([t.c.id]).where(t.c.name == name)

        content_type_id=DBSession.execute(q).scalar()

        if not content_type_id:
            raise ValueError('Missing content type: %s' % name)

        return content_type_id

    ###########
    # MAPPERS #
    ###########

    # ** Hint:
    # What kind of loading to use for large collections?
    #
    # One to Many Collection:
    # joined eager loading only makes sense when the size of the collections
    # are relatively small.
    # subquery load makes sense when the collections are larger.
    #
    # Many to One Reference:
    # there’s probably not much advantage of using subquery loading here over
    # joined loading.

    orm.mapper(ContentType, table['content_type'])

    orm.mapper(Country, table['country'])

    orm.mapper(State, table['state'])

    orm.mapper(Tag, table['tag'])

    orm.mapper(Account, table['account'],
        properties={
            'count_content': orm.column_property(
                sql.select(
                    [sql.func.count()],
                    table['account'].c.id == table['content'].c.owner_id
                ).label('count_content'),
                deferred=True
            )
        })

    orm.mapper(MimeMajor, table['mime_major'])

    orm.mapper(Mime, table['mime'],
        properties={
            'major': orm.relationship(MimeMajor, lazy='joined')
        })

    # Joined table inheritance is used.
    _count_alias=table['content'].alias('_count_children')
    orm.mapper(Content, table['content'],
        polymorphic_on=table['content'].c.content_type_id,
        properties={

            # no need to load this column by default
            'fts': orm.deferred(table['content'].c.fts),

            #################
            # RELATIONSHIPS #
            #################

            'owner': orm.relationship(
                Account,
                lazy='joined',
                innerjoin=True,
                backref=orm.backref('contents', lazy='dynamic',
                                      cascade='all, delete-orphan')
            ),

            'state': orm.relationship(
                State,
                lazy='joined',
                innerjoin=True
            ),

            'type': orm.relationship(
                ContentType,
                lazy='joined',
                innerjoin=True
            ),

            'tags': orm.relationship(
                Tag,
                secondary=table['content_tag']
            ),

            'parent': orm.relationship(
                Folder,
                foreign_keys=table['content'].c.container_id,
                innerjoin=True,
                uselist=False,
                backref=orm.backref('children', cascade='all, delete-orphan')
            ),

            #####################
            # COLUMN PROPERTIES #
            #####################

            # TODO: move this to Folder class
            'count_children': orm.column_property(
                sql.select([sql.func.count()]).where(
                    _count_alias.c.container_id == table['content'].c.id
                ).correlate(table['content']).label('count_children'),
                deferred=True
            ),

            'position_in_container': orm.column_property(
                sql.func.row_number().\
                over(partition_by=table['content'].c.container_id,
                     order_by=table['content'].c.weight.desc()),
                deferred=True,
                group='window_func'
            )

        })

    orm.mapper(File, table['data'], inherits=Content,
        polymorphic_identity=_get_type_id('file'),
        inherit_condition=table['data'].c.content_id ==
                          table['content'].c.id,
        properties={
            'mime': orm.relationship(
                Mime,
                lazy='joined'
            )
        })

    orm.mapper(Event, table['event'], inherits=Content,
        polymorphic_identity=_get_type_id('event'),
        properties={
            'country': orm.relationship(Country, lazy='joined')
        })

    orm.mapper(Folder, table['folder'], inherits=Content,
        polymorphic_identity=_get_type_id('folder'),
        inherit_condition=table['folder'].c.content_id ==
               table['content'].c.id,
        properties={
            'alternate_index': orm.relationship(
                Content,
                primaryjoin=table['folder'].c.index_content_id ==
                table['content'].c.id,

                innerjoin=True,
                uselist=False,
                post_update=True,
                backref=orm.backref('indexes')
            ),

            'polymorphic_children': orm.relationship(
                ContentType,
                secondary=table['folder_polymorphic_loading']
            )
        }
    )

    orm.mapper(Page, table['page'], inherits=Content,
               polymorphic_identity=_get_type_id('page'))

    orm.mapper(News, table['news'], inherits=Content)

    ###################
    # EVENT LISTENERS #
    ###################

    sa_event.listen(Content, 'before_update', update_updated_listener,
                    propagate=True)

    sa_event.listen(Content, 'before_insert', update_FTS_listener,
                    propagate=True)

    sa_event.listen(Content, 'before_update', update_FTS_listener,
                    propagate=True)

    ###################
    # FULLTEXT SEARCH #
    ###################

    Content._FTS_ = (('title', 'A'), ('description', 'B'))
    News._FTS_ = (('title', 'A'), ('description', 'B'), ('body', 'C'))
    Page._FTS_ = (('title', 'A'), ('description', 'B'), ('body', 'C'))
    Event._FTS_ = (('title', 'A'), ('description', 'B'), ('location', 'B'),
                   ('address', 'B'), ('body', 'C'))

    ####################
    # ALLOWED ORDERING #
    ####################

    from amnesia.order import EntityOrder, Path

    orders.update({
        'title': EntityOrder(Content, 'title', 'asc', doc='title'),

        'weight': EntityOrder(Content, 'weight', 'desc', doc='default'),

        'update': EntityOrder(Content, 'last_update', 'desc',
                              doc='last update'),

        'added': EntityOrder(Content, 'added', 'desc', doc='added date'),

        'type': EntityOrder(ContentType, 'name', 'asc', path=[Path(Content,
                                                                   'type')],
                            doc='content type'),

        'owner': EntityOrder(Account, 'full_name', 'asc', path=[Path(Content,
                                                                     'owner')],
                             doc='owner'),

        'starts': EntityOrder(Event, 'starts', 'desc', doc='event starts'),

        'ends': EntityOrder(Event, 'ends', 'desc', doc='event ends'),

        'country': EntityOrder(Country, 'name', 'asc', path=[Path(Event,
                                                                  'country')],
                               doc='event country'),

        'major': EntityOrder(MimeMajor, 'name', 'asc',
                             path=[Path(File, 'mime'), Path(Mime, 'major')],
                             doc='mime')
    })
