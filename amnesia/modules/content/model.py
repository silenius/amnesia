# pylint: disable=E1101

import typing as t

from datetime import datetime

from pytz import timezone

from sqlalchemy import sql
from sqlalchemy import orm
from sqlalchemy.types import Interval
from sqlalchemy.types import DateTime
from sqlalchemy.ext.hybrid import hybrid_property

from .. import Base


class Content(Base):
    """This is the base class for all the different types of Content (Event,
        News, Page, etc)"""

    # FIXME: make this plugable
    _FTS_ = (('title', 'A'), ('description', 'B'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}:{self.id}>'

#    def format(self, format, **kwargs):
#        serializer = Serializer(self)
#        return getattr(serializer, format)(**kwargs)

    __str__ = __repr__

    @property
    def fa_icon(self) -> t.Optional[str]:
        try:
            return self.type.icons['fa']
        except (TypeError, KeyError):
            return None

    @classmethod
    def cls_from_identity(cls, ident):
        mapper = orm.class_mapper(cls).base_mapper

        if ident is not None:
            return mapper.polymorphic_map[ident].class_

        return mapper.class_

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
    def filter_published(cls, timez='UTC'):
        today = datetime.now(tz=timezone(timez))

        return sql.and_(
            cls.filter_effective(today=today),
            cls.filter_expiration(today=today)
        )

    @classmethod
    def filter_effective(cls, today=None, timez='UTC'):
        """Select items for which the effective date has been reached"""
        if not today:
            today = datetime.today()

        return sql.func.coalesce(
            cls.effective,
            sql.cast('-infinity', DateTime(timezone=timez))
        ) <= today

    @classmethod
    def filter_expiration(cls, today=None, timez='UTC'):
        """Select items for which the expiration date has not been reached"""
        if today is None:
            today = datetime.today()

        return sql.func.coalesce(
            cls.expiration,
            sql.cast('infinity', DateTime(timezone=timez))
        ) >= today

    @classmethod
    def filter_container_id(cls, container_id):
        """Select items which are in a specific container"""
        return cls.container_id == container_id

    @classmethod
    def filter_modified(cls, part, col=None):
        if col is None:
            col = cls.last_update

        return sql.and_(
            col >= sql.func.date_trunc(part, sql.func.now()),
            col < sql.func.date_trunc(part, sql.func.now()) +
            sql.cast('1 {}'.format(part), Interval)
        )

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
