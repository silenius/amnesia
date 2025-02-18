import secrets
import logging

from pyramid.authentication import AuthTktCookieHelper
from pyramid.authorization import ACLHelper
from pyramid.authorization import Authenticated
from pyramid.authorization import Everyone
from pyramid.interfaces import ICSRFStoragePolicy
from pyramid.request import RequestLocalCache
from pyramid.settings import asbool
from pyramid.util import (
    bytes_,
    text_,
    strings_differ,
)

from sqlalchemy import sql

from zope.interface import implementer


__all__ = ['cookie_security_policy']

log = logging.getLogger(__name__)


def cookie_security_policy(settings):
    cfg = {
        'http_only': asbool(settings.get('auth.http_only', 'true')),
        'secure': asbool(settings.get('auth.secure', 'false')),
        'secret': settings['auth.secret'],
    }

    helper = AmnesiaAuthTktCookieHelper(**cfg)

    return AmnesiaSecurityPolicy(helper)


class AmnesiaAuthTktCookieHelper(AuthTktCookieHelper):

    def userid(self, request):
        identity = self.identify(request)
        return None if identity is None else identity['userid']


class AmnesiaSecurityPolicy:

    def __init__(self, helper):
        self.helper = helper
        self.identity_cache = RequestLocalCache(self.load_user)
        self.acl = ACLHelper()

    def load_user(self, request):
        userid = self.helper.userid(request)

        if userid:
            from amnesia.modules.account import Account

            user = request.dbsession.execute(
                sql.select(Account).filter_by(id=userid, enabled=True)
            ).scalar_one_or_none()

            return user

        return None

    def identity(self, request):
        return self.identity_cache.get_or_create(request)

    def authenticated_userid(self, request):
        """ Return a string ID for the user. """

        identity = self.identity(request)
        return None if identity is None else str(identity.id)

    def remember(self, request, userid, **kwargs):
        return self.helper.remember(request, userid, **kwargs)

    def forget(self, request, **kwargs):
        return self.helper.forget(request, **kwargs)

    def permits(self, request, context, permission):
        principals = self.effective_principals(request, context)
        return self.acl.permits(context, principals, permission)

    def effective_principals(self, request, context):
        principals = {Everyone}
        user = self.identity(request)

        if user is not None:
            principals.add(Authenticated)
            principals.add(f'u:{user.id}')

            for role in user.roles:
                if role.virtual:
                    principals.add(role.name)
                else:
                    principals.add(f'r:{role.name}')

        if hasattr(context, '__effective_principals__'):
            context_principals = context.__effective_principals__

            if callable(context_principals):
                context_principals = context_principals()

            if context_principals:
                principals.update(context_principals)

        return list(principals)



@implementer(ICSRFStoragePolicy)
class HttpHeaderCSRFStoragePolicy:
    """A CSRF storage policy that persists the CSRF token in an HTTP header.

    ``header_name``

        The header name here the CSRF token will be stored.
        Default: `X-CSRF-Token`.

    """

    _token_factory = staticmethod(lambda: text_(secrets.token_hex()))

    def __init__(self, header_name='X-CSRF-Token'):
        self.header_name = header_name

    def new_csrf_token(self, request):
        """Sets a new CSRF token into the header and returns it."""
        token = self._token_factory()
        request.headers[self.header_name] = token

        def set_header(request, response):
            response.headers.add(self.header_name, token)

        request.add_response_callback(set_header)
        
        return token

    def get_csrf_token(self, request):
        """Returns the currently active CSRF token from the header,
        generating a new one if needed."""
        token = request.headers.get(self.header_name)

        if not token:
            token = self.new_csrf_token(request)
        
        return token

    def check_csrf_token(self, request, supplied_token):
        """Returns ``True`` if the ``supplied_token`` is valid."""
        expected_token = self.get_csrf_token(request)

        return not strings_differ(
            bytes_(expected_token), bytes_(supplied_token)
        )
