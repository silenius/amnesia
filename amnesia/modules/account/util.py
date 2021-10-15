# -*- coding: utf-8 -*-

import bcrypt

from pyramid.security import Deny
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS


def bcrypt_hash_password(pw):
    pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
    return pwhash.decode('utf8')


def bcrypt_check_password(pw, hashed_pw):
    expected_hash = hashed_pw.encode('utf8')
    return bcrypt.checkpw(pw.encode('utf8'), expected_hash)


def to_pyramid_acl(acl):
    permission = acl.permission.name
    allow_or_deny = Allow if acl.allow else Deny
    role = acl.role.name if acl.role.virtual else f'r:{acl.role.name}'

    if permission == 'ALL_PERMISSIONS':
        permission = ALL_PERMISSIONS

    return (allow_or_deny, role, permission)
