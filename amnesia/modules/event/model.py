from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

from amnesia.modules.content import Content


# pylint: disable=no-member
class Event(Content):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
