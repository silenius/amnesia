# -*- coding: utf-8 -*-

from sqlalchemy import sql
from sqlalchemy.orm.exc import NoResultFound

from amnesia import db
from amnesia.models.root import RootModel


class MimeMajor(RootModel):

    def __init__(self, **kwargs):
        super(MimeMajor, self).__init__(**kwargs)


class Mime(RootModel):

    def __init__(self, **kwargs):
        super(Mime, self).__init__(**kwargs)

    @property
    def name(self):
        return '%s/%s' % (self.major.major, self.minor)

    @staticmethod
    def q_major_minor(major, minor):
        try:
            return Mime.query.join(MimeMajor).\
                   filter(Mime.minor == minor).\
                   filter(MimeMajor.major == major).\
                   one()
        except NoResultFound:
            return None

    ###########
    # Filters #
    ###########

    @classmethod
    def filter_mime(cls, value):
        (major, minor) = value.split('/')
        cond = sql.and_()
        cond.append(MimeMajor.major == major)
        if minor and minor != '*':
            cond.append(Mime.minor == minor)
        return cond
