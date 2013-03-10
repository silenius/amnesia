# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import sql

from amnesia import db
from amnesia.models import content


class EventQuery(content.ContentQuery):

    def __init__(self, *args, **kwargs):
        super(EventQuery, self).__init__(*args, **kwargs)


class Event(content.Content):

    query = db.Session.query_property(EventQuery)

    FTS = [('title', 'A'), ('description', 'B'), ('location', 'B'), 
           ('address', 'B'), ('body', 'C')]

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

    @property
    def duration(self):
        duration = (self.ends - self.starts).days + 1
        if duration > 1:
            return '%s days' % duration
        elif duration == 1:
            return '%s day' % duration
        else:
            return None

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

    @classmethod
    def filter_starts_within(cls, month, year):
        return sql.and_(sql.func.date_part('year', cls.starts) == year,
                        sql.func.date_part('month', cls.starts) == month)
