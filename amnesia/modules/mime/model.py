# pylint: disable=E1101

from sqlalchemy import sql

from .. import Base

# http://www.iana.org/assignments/media-types/media-types.xhtml


class MimeMajor(Base):
    """Mime major"""

    def __init__(self, name):
        super().__init__()
        self.name = name


class Mime(Base):

    def __init__(self, name, template, major):
        super().__init__()
        self.name = name
        self.template = template
        self.major = major

    @property
    def full(self):
        return '{0}/{1}'.format(self.major.name, self.name)

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
