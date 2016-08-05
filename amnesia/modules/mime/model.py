# -*- coding: utf-8 -*-

from sqlalchemy import sql
from sqlalchemy import orm

from sqlalchemy.orm.exc import NoResultFound

from .. import Base

# http://www.iana.org/assignments/media-types/media-types.xhtml


class MimeMajor(Base):

    """Mime major"""


class Mime(Base):

    @property
    def full(self):
        return '%s/%s' % (self.major.name, self.name)

    @staticmethod
    def q_major_minor(major, minor):
        cond = sql.and_(MimeMajor.name == major,
                        Mime.name == minor)
        try:
            return Mime.query.join(Mime.major).\
                   options(orm.contains_eager(Mime.major)).\
                   filter(cond).one()
        except NoResultFound:
            return None

    ###########
    # Filters #
    ###########

    @classmethod
    def filter_mime(cls, value):
        (major, minor) = value.split('/')
        cond = sql.and_()
        cond.append(MimeMajor.name == major)
        if minor and minor != '*':
            cond.append(Mime.name == minor)
        return cond
