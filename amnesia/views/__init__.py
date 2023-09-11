from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from amnesia.utils.locale import get_locale_url
from amnesia.utils.request import RequestMixin

def includeme(config):
    config.include('.haproxy')
    config.include('.index')
    config.include('.contact')

    config.scan(__name__)


class BaseView(RequestMixin):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def schema(
        self, factory, *, exclude=None, extra_context=None,
        unknown=None, only=None
    ):
        context = {
            'request': self.request, 
            'context': self.context
        }

        if extra_context:
            context |= extra_context

        if exclude is None:
            exclude = []

        exclude = [f for f in exclude if f in factory._declared_fields]

        return factory(
            context=context,
            exclude=exclude,
            unknown=unknown,
            only=only
        )


@view_config(name='change_locale')
def change_locale(request):
    lang = request.GET.getone('lang')
    location = get_locale_url(lang, request)

    return HTTPFound(location)
