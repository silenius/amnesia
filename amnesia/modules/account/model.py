# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy.ext.hybrid import hybrid_property

from .util import bcrypt_hash_password

from .. import Base


class Account(Base):

    def __init__(self, password, **kwargs):
        self.password = bcrypt_hash_password(password)
        super().__init__(**kwargs)

    @hybrid_property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.name)
