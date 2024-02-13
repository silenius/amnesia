import logging
import typing as t

from pyramid.response import (
    Response,
    FileResponse
)

from pyramid.request import Request

from pyramid.view import view_config

from pyramid.httpexceptions import HTTPNotFound


from amnesia.modules.file import FileEntity


log = logging.getLogger(__name__)

def includeme(config):
    config.scan(__name__)


@view_config(
    context=FileEntity,
    name='download',
    request_method='GET',
    permission='read'
)
def download(
        context: FileEntity, 
        request: Request
    ) -> t.Union[Response, FileResponse]:

    try:
        file_response = context.serve(disposition='attachment')
    except FileNotFoundError:
        raise HTTPNotFound()

    return file_response



