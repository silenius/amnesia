# -*- coding: utf-8 -*-

from amnesia.models.root import RootModel

from sqlalchemy.ext.hybrid import hybrid_property


class Account(RootModel):

    @hybrid_property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)
