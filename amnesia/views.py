from pyramid.response import Response
from pyramid.view import view_config
from pyramid.view import view_defaults

from sqlalchemy.exc import DBAPIError

from .models import DBSession

from amnesia.resources import FolderResource
from amnesia.resources import ContentResource
from amnesia.resources import PageResource


@view_defaults(context=ContentResource)
class RESTContent:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(request_method='DELETE')
    def delete(self):
        return Response('DELETE')


@view_defaults(context=FolderResource)
class RESTFolder(RESTContent):

    @view_config(name='post')
    def POST(self):
        return Response('POST')


@view_defaults(context=PageResource)
class RESTPage(RESTContent):
    """ REST Page """

    @view_config(request_method='GET', accept='text/html',
                 renderer='templates/page/show.pt')
    def get(self):
        return {'item': self.context.obj}
