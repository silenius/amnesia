from pyramid.httpexceptions import HTTPNoContent
from pyramid.security import forget
from pyramid.view import view_config

from amnesia.modules.account import AuthResource


def includeme(config):
    config.scan(__name__)


@view_config(
    name='logout',
    context=AuthResource,
    permission='logout',
    request_method='POST'
)
def logout(context, request):
    headers = forget(request)
    request.session.invalidate()
    return HTTPNoContent(headers=headers)
