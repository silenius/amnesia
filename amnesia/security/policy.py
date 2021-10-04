import logging

from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper
from pyramid.authorization import Authenticated
from pyramid.authorization import Everyone
from pyramid.request import RequestLocalCache
from pyramid.settings import asbool

from sqlalchemy import sql

from amnesia.modules.account import Account

__all__ = ['cookie_security_policy']

log = logging.getLogger(__name__)


def cookie_security_policy(settings):
    cfg = {
        'debug': asbool(settings.get('auth.debug', 'false')),
        'http_only': asbool(settings.get('auth.http_only', 'true')),
        'secure': asbool(settings.get('auth.secure', 'false')),
        'secret': settings['auth.secret'],
    }

    helper = AuthTktCookieHelper(**cfg)

    return AmnesiaSecurityPolicy(helper)


class AmnesiaSecurityPolicy:

    def __init__(self, helper):
        self.helper = helper
        self.identity_cache = RequestLocalCache(self.load_user)
        self.acl = ACLHelper()

    def load_user(self, request):
        identity = self.helper.identify(request)

        if identity is None:
            return None

        userid = identity['userid']

        user = request.dbsession.execute(
            sql.select(Account).filter_by(id=userid, enabled=True)
        ).scalar_one_or_none()

        return user

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        """ Return a string ID for the user. """

        identity = self.identity(request)

        if identity is None:
            return None

        return str(identity.id)

    def remember(self, request, userid, **kw):
        return self.helper.remember(request, userid, **kw)

    def forget(self, request, **kw):
        return self.helper.forget(request, **kw)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request, context)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request, context):
        principals = [Everyone]
        user = self.identity(request)

        if user is not None:
            principals.append(Authenticated)
            principals.append(str(user.id))

            for role in user.roles:
                if role.virtual:
                    principals.append(role.name)
                else:
                    principals.append('role:{}'.format(role.name))

        return principals
