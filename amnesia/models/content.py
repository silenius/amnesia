# -*- coding: utf-8 -*-

import itertools

from datetime import datetime

import cherrypy

from sqlalchemy import sql, orm
from sqlalchemy.util import OrderedSet

from amnesia import db

from amnesia.models import root
from amnesia.models.state import State
from amnesia.models.auth import Human
from amnesia.models.tag import Tag


class ContentQuery(root.RootQuery):
    """Default Query object"""

    def __init__(self, *args, **kwargs):
        super(ContentQuery, self).__init__(*args, **kwargs)


class Content(root.RootModel):
    """This is the base class for all the different types of Content (Event,
        News, Page, etc)"""

    query = db.Session.query_property(ContentQuery)

    # Full text search columns
    FTS = [('title', 'A'), ('description', 'B')]

    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)

    def last_update(self, format=None):
        # FIXME
        format = "%Y-%m-%d at %H:%M"
        if format is None:
            format = config['timestamp_format']

        return self.updated.strftime(format) if self.updated else\
                                                self.added.strftime(format)

    def url_for(self, action='show'):
        if action in ('show', 'index', None):
            return cherrypy.url('/%s' % self.id)
        elif action:
            return cherrypy.url('/%s/%s' % (self.id, action))
        else:
            return cherrypy.url('/notfound')

    def type_icon(self, size='16x16'):
        return cherrypy.url('/images/content_types/%s/%s' % (size, str(self.type.icon)))

    def get_full_polymorphic_tree(self, polymorphic_map=None):
        """Returns the full class hierarchy (in correct order) with a given 
           list of polymorphic identities. The returned list can be used with
           the with_polymorphic() Query's method."""

        if not self.polymorphic_loading:
            # TODO: check default polymorphic loading strategy (config ?)
            return None
        elif self.polymorphic_loading == 'n':
            # No polymorphic loading
            return None
        elif self.polymorphic_loading == 'y':
            # Polymorphic loading of _all_ mappers
            return '*'
        elif self.polymorphic_loading == 'c':
            # Polymorphic loading of _some_ mappers. The polymorphic_identity
            # is the content_type.id, so we have to retrieve all the
            # primary mappers for those content_type.id. 
            # This can be found in the .polymorphic_map property of the 
            # root mapper (Content)
            if not polymorphic_map:
                polymorphic_map = orm.class_mapper(self.__class__).\
                                  polymorphic_map

            # At this time of writing, when you have more the one level of
            # inheritance SQLAlchemy doesn't add the classes which don't
            # have a polymorphic_identity .. so there is a missing JOIN.
            # I use .iterate_to_root() to bypass the problem.
            # Also, classes must be in the right order for the 
            # with_polymorphic() function, otherwise SQLAlchemy joins
            # tables in the wrong order. 
            # I've added a ticket on the SQLAlchemy trac: 
            # http://www.sqlalchemy.org/trac/ticket/1900
            #
            # TODO: could be replaced with .self_and_descendants (?)
            return list(OrderedSet(itertools.chain(
                *[reversed(list(polymorphic_map[identity].iterate_to_root()))\
                for identity in [ct.id for ct in self.polymorphic_children]])))
        else:
            raise ValueError(self.polymorphic_loading)

    ###########
    # Filters #
    ###########

    @classmethod
    def filter_published(cls):
        today = datetime.today()
        return sql.and_(cls.filter_effective(today=today), 
                        cls.filter_expiration(today=today))

    @classmethod
    def filter_effective(cls, today=None, strict=False):
        """Select items for which the effective date has been reached"""
        if not today:
            today = datetime.today()
        cond = cls.effective <= today
        return cond if strict else sql.or_(cond, cls.effective == None)

    @classmethod
    def filter_expiration(cls, today=None, strict=False):
        """Select items for which the expiration date has not been reached"""
        if not today:
            today = datetime.today()
        cond = cls.expiration >= today
        return cond if strict else sql.or_(cond, cls.expiration == None)

    @classmethod
    def filter_in_container(cls, container_id):
        """Select items which are in a specific container"""
        return cls.container_id == container_id

    @classmethod
    def filter_only_mine(cls):
        """Select items from a authenticated user"""
        try:
            user_id = int(cherrypy.session[config['session_login_key']])
        except KeyError:
            pass
        else:
            return cls.owner_id == user_id

    @classmethod
    def filter_date_trunc(cls, part, col=None):
        """Helper function to extract the day or week or month from
           Content.updated or Content.added (if Content.updated is NULL), and
           compare this value to the current_date()"""
        if not col: 
            col = sql.func.coalesce(cls.updated, cls.added)
        return sql.func.date_trunc(part, col) == \
               sql.func.date_trunc(part, sql.func.current_date())

    @classmethod
    def filter_modified_today(cls):
        """Select items which have been modified today"""
        return cls.filter_date_trunc('day')

    @classmethod
    def filter_modified_week(cls):
        """Select items which have been modified this week"""
        return cls.filter_date_trunc('week')

    @classmethod
    def filter_modified_month(cls):
        """Select items which have been modified this month"""
        return cls.filter_date_trunc('month')

    @classmethod
    def filter_perm_view(cls, human_obj=None):
        """Select items which can be viewed by human_obj"""
        if human_obj is not None:
            return sql.or_(State.name == 'published',
                           cls.owner_id == human_obj.id,
                           human_obj.has_perm(('manager', 'view content')),
                           sql.and_(State.name == 'pending',
                                    human_obj.has_perm('change state')))
        else:
            return State.name == 'published'

    @classmethod
    def filter_tag(cls, tag):
        """Select items which have a specific tag"""
        table = db.meta.tables
        return sql.exists([1], from_obj=[table['tag'].join(table['content_tag'])]).\
               where(sql.and_(cls.id == table['content_tag'].c.content_id,
                              sql.func.lower(tag) == sql.func.lower(Tag.name)))
