from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from amnesia.utils.locale import get_locale_url

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
    location = get_locale_url(lang, request)

    return HTTPFound(location)
