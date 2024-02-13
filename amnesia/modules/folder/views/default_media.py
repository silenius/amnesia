import logging

from pyramid.httpexceptions import HTTPNotFound
from pyramid.request import Request
from pyramid.view import view_config

from amnesia.views import BaseView
from amnesia.modules.folder import FolderResource
from amnesia.modules.folder.validation import FolderSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_config(
    context=FolderResource,
    name='default_media',
    request_method='GET',
    renderer='json'
)
class get_default_media(BaseView):
    def __call__(self):
        folder = self.context.get_default_media()

        if folder is None:
            raise HTTPNotFound()

        return self.schema(FolderSchema).dump(folder)
