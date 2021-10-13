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
        yield Allow, 'r:Manager', ALL_PERMISSIONS

        from amnesia.modules.account.security import get_global_acl

        for acl in get_global_acl(self.request):
            yield from self.__acl_adapter__(acl.to_pyramid_acl())

        # Note: if there's no explicit permission, the default is to DENY so in
        # theory there is no need for a yield DENY_ALL (but keep it just to be
        # sure)

        yield DENY_ALL

    def __acl_adapter__(self, ace):
        yield ace

    @property
    def extra_paths(self):
        try:
            return self.request.registry.cms_resource_paths[self.__class__]
        except (KeyError, AttributeError):
            return {}

    @property
    def dbsession(self):
        ''' Database session '''
        return self.request.dbsession

    @property
    def settings(self):
        ''' Pyramid registry settings '''
        return self.request.registry.settings
