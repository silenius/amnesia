# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from ..content import Content
from ..content import ContentTranslation


class EventTranslation(ContentTranslation):
    ''' Holds translations '''


# pylint: disable=no-member
class Event(Content):

    def __init__(self, **kwargs):
        super(Event, self).__init__(**kwargs)

    @property
    def finished(self):
        return self.ends < datetime.today()

    @property
    def has_begin(self):
        return self.starts <= datetime.today()

    @property
    def georeferenced(self):
        return self.address_latitude != None and \
               self.address_longitude != None

    @hybrid_property
    def body(self):
        return self.current_translation.body

    @body.setter
    def body(self, value):
        self.current_translation.body = value

    ###########
    # FILTERS #
    ###########

    @classmethod
    def filter_not_finished(cls, timestamp=None):
        if not timestamp:
            timestamp = datetime.today()

        return cls.ends >= timestamp

    @classmethod
    def filter_finished(cls, timestamp=None):
        if not timestamp:
            timestamp = datetime.today()

        return cls.ends < timestamp
