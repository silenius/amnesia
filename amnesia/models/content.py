# -*- coding: utf-8 -*-

from datetime import datetime

import cherrypy

from sqlalchemy import sql, orm
from sqlalchemy.util import OrderedSet
from sqlalchemy.types import Interval

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

    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)

    def __repr__(self):
        return "<{}, id={}>".format(self.__class__.__name__, self.id)

    __str__ = __repr__

    def url_for(self, action='show'):
        if action in ('show', 'index', None):
            return cherrypy.url('/%s' % self.id)
        elif action:
            return cherrypy.url('/%s/%s' % (self.id, action))
        else:
            return cherrypy.url('/notfound')

    def type_icon(self, size='16x16'):
        return cherrypy.url('/images/content_types/%s/%s' % (size, str(self.type.icon)))

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
            # FIXME config is undefined
            user_id = int(cherrypy.session[config['session_login_key']])
        except KeyError:
            pass
        else:
            return cls.owner_id == user_id

    @classmethod
    def filter_modified(cls, part, col=None):
        if col is None:
            col = cls.last_update

        return sql.and_(col >= sql.func.date_trunc(part, sql.func.now()),
                        col < sql.func.date_trunc(part, sql.func.now())\
                              + sql.cast('1 %s' % part, Interval))

    @classmethod
    def filter_modified_today(cls):
        """Select items which have been modified today"""
        return cls.filter_modified('day')

    @classmethod
    def filter_modified_week(cls):
        """Select items which have been modified this week"""
        return cls.filter_modified('week')

    @classmethod
    def filter_modified_month(cls):
        """Select items which have been modified this month"""
        return cls.filter_modified('month')

    @classmethod
    def filter_tag(cls, tag):
        """Select items which have a specific tag"""
        table = db.meta.tables
        return sql.exists([1], from_obj=[table['tag'].join(table['content_tag'])]).\
               where(sql.and_(cls.id == table['content_tag'].c.content_id,
                              sql.func.lower(tag) == sql.func.lower(Tag.name)))
