# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy.ext.hybrid import hybrid_property

from .util import bcrypt_hash_password
from amnesia.modules.account.util import to_pyramid_acl

from .. import Base


class Account(Base):

    def __init__(self, password, **kwargs):
        self.password = bcrypt_hash_password(password)
        super().__init__(**kwargs)

    @hybrid_property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Role(Base):

    def __init__(self, name, description=None):
        self.name = name
        self.description = description


class AccountRole(Base):

    def __init__(self, account, role):
        self.account = account
        self.role = role


class Permission(Base):

    def __init__(self, name, description=None):
        self.name = name
        self.description = description


class ACLResource(Base):

    def __init__(self, name):
        self.name = name


class ACL(Base):

    def __init__(self, role, permission, allow):
        self.role = role
        self.permission = permission
        self.allow = allow

    def to_pyramid_acl(self):
        return to_pyramid_acl(self)


class GlobalACL(ACL):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContentACL(ACL):

    def __init__(self, content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content = content
