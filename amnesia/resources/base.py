# -*- coding: utf-8 -*-

import logging

from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL

log = logging.getLogger(__name__)


class Resource:
    ''' Base resource class. All other resources should inherit from it. '''

    def __init__(self, request):
        self.request = request

    def __acl__(self):
        yield Allow, 'role:Manager', ALL_PERMISSIONS

        # Note: if there's no explicit permission, the default is to DENY so in
        # theory there is no need for a yield DENY_ALL (but keep it just to be
        # sure)
        from amnesia.modules.account.security import get_global_acl

        for acl in get_global_acl(self.request):
            perm = acl.permission.name
            allow_deny = Allow if acl.allow else Deny

            if acl.role.is_virtual():
                role = acl.role.name
            else:
                role = 'role:{}'.format(acl.role.name)

            yield from self.__acl_adapter__(allow_deny, role, perm)

        yield DENY_ALL

    def __acl_adapter__(self, allow_deny, role, perm):
        yield allow_deny, role, perm

    @property
    def dbsession(self):
        ''' Database session '''
        return self.request.dbsession

    @property
    def settings(self):
        ''' Pyramid registry settings '''
        return self.request.registry.settings
