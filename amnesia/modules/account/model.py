# -*- coding: utf-8 -*-

from .. import Base

from sqlalchemy.ext.hybrid import hybrid_property


class Account(Base):

    @hybrid_property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
