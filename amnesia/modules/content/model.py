# -*- coding: utf-8 -*-

from datetime import datetime

from pytz import timezone
from sqlalchemy import sql, orm
from sqlalchemy.types import Interval, DateTime
from sqlalchemy.ext.hybrid import hybrid_property

from amnesia.models.root import RootModel
from .state import State
from .account import Account
from .tag import Tag


class Content(RootModel):
    """This is the base class for all the different types of Content (Event,
        News, Page, etc)"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return u"<{0}:{1} ({2})>".format(self.__class__.__name__, self.id,
                                         self.title)

    __str__ = __repr__

    @classmethod
    def cls_from_identity(cls, ident):
        m = orm.class_mapper(cls).base_mapper

        if ident is not None:
            return m.polymorphic_map[ident].class_
        else:
            return m.class_

    @hybrid_property
    def last_update(self):
        return self.updated if self.updated else self.added

    @last_update.expression
    def last_update(cls):
        return sql.func.coalesce(cls.updated, cls.added)

    ###########
    # Filters #
    ###########

    @classmethod
    def filter_published(cls):
        today = datetime.now(tz=timezone('Europe/Brussels'))

        #TODO: use the new 9.2 range type
        return sql.and_(cls.filter_effective(today=today),
                        cls.filter_expiration(today=today))

    @classmethod
    def filter_effective(cls, today=None):
        """Select items for which the effective date has been reached"""
        if not today:
            today = datetime.today()

        return sql.func.coalesce(
            cls.effective,
            sql.cast('-infinity', DateTime(timezone('Europe/Brussels')))
        ) <= today

    @classmethod
    def filter_expiration(cls, today=None):
        """Select items for which the expiration date has not been reached"""
        if not today:
            today = datetime.today()

        return sql.func.coalesce(
            cls.expiration,
            sql.cast('infinity', DateTime(timezone='Europe/Brussels'))
        ) >= today

    @classmethod
    def filter_in_container(cls, container_id):
        """Select items which are in a specific container"""
        return cls.container_id == container_id

    @classmethod
    def filter_only_mine(cls):
        """Select items from a authenticated user"""
        try:
            user_id = int(cherrypy.session[cherrypy.request.config['session_login_key']])
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
