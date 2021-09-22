from urllib.parse import urljoin

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

def includeme(config):
    config.include('.haproxy')
    config.include('.index')
    config.include('.contact')

    config.scan(__name__)


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def dbsession(self):
        return self.request.dbsession


@view_config(name='change_locale')
def change_locale(request):
    lang = request.GET.getone('lang')

    location = urljoin(
        request.resource_url(
            request.root
        ).rsplit(
            request.locale_name, 1
        )[0],
        lang
    )

    return HTTPFound(location)
