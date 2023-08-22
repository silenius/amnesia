# pylint: disable=E1101

from sqlalchemy.ext.hybrid import hybrid_property

from amnesia.modules.account.utils import to_pyramid_acl

from .utils import bcrypt_hash_password

from .. import Base


class Account(Base):

    def __init__(self, password, **kwargs):
        self.password = bcrypt_hash_password(password)
        super().__init__(**kwargs)

    @hybrid_property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class AccountAuditLogin(Base):

    def __init__(self, account, ip, success, ts=None, info=None):
        self.account = account
        self.ts = ts
        self.ip = ip
        self.success = success
        self.info = info


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_pyramid_acl(self):
        return to_pyramid_acl(self)


class GlobalACL(ACL):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ContentACL(ACL):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
