import logging

from pyramid.request import RequestLocalCache
from pyramid.authorization import Allow
from pyramid.authorization import ALL_PERMISSIONS
from pyramid.authorization import DENY_ALL

log = logging.getLogger(__name__)


@RequestLocalCache()
def load_global_acl(request):
    from amnesia.modules.account.security import get_global_acl
    return get_global_acl(request.dbsession, request.identity)


class Resource:
    ''' Base resource class. All other resources should inherit from it. '''

    def __init__(self, request):
        self.request = request

    def __acl__(self):
        yield Allow, 'r:Manager', ALL_PERMISSIONS

        for acl in load_global_acl(self.request):
            yield acl.to_pyramid_acl()

        # Note: if there's no explicit permission, the default is to DENY so in
        # theory there is no need for a yield DENY_ALL (but keep it just to be
        # sure)

        yield DENY_ALL

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
