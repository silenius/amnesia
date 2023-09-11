import logging

from pyramid.request import RequestLocalCache
from pyramid.authorization import Allow
from pyramid.authorization import ALL_PERMISSIONS
from pyramid.authorization import DENY_ALL

from amnesia.utils.request import RequestMixin

log = logging.getLogger(__name__)


@RequestLocalCache()
def load_global_acl(request):
    from amnesia.modules.account.security import get_global_acl
    stmt = get_global_acl(request.identity)
    return request.dbsession.scalars(stmt).all()


class Resource(RequestMixin):
    ''' Base resource class. All other resources should inherit from it. '''

    def __init__(self, request):
        self.request = request

    def __acl__(self, raw=False):
        if not raw:
            yield Allow, 'r:Manager', ALL_PERMISSIONS

        for acl in load_global_acl(self.request):
            yield acl if raw else acl.to_pyramid_acl()

        # Note: if there's no explicit permission, the default is to DENY so in
        # theory there is no need for a yield DENY_ALL (but keep it just to be
        # sure)

        if not raw:
            yield DENY_ALL

    @property
    def extra_paths(self):
        try:
            return self.registry.cms_resource_paths[self.__class__]
        except (KeyError, AttributeError):
            return {}
