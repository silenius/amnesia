import logging
import typing as t

from marshmallow import ValidationError

from pyramid.view import (
    view_config,
    view_defaults
)

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPNoContent,
    HTTPInternalServerError,
    HTTPNotAcceptable
)

from pyramid.response import (
    Response,
    FileResponse
)

from pyramid.request import Request

from amnesia.modules.folder import FolderEntity
from amnesia.modules.file import File
from amnesia.modules.file import utils as file_utils
from amnesia.modules.file import FileEntity
from amnesia.modules.file import ImageFileEntity
from amnesia.modules.file.validation import FileSchema
from amnesia.modules.file.events import FileUpdated
from amnesia.modules.file.exc import UnsupportedFormatError
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)  # pylint: disable=C0103

def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


@view_config(
    context=FileEntity,
    name='download',
    request_method='GET',
    permission='read'
)
def download(context: FileEntity, 
             request: Request
    ) -> t.Union[Response, FileResponse]:
    try:
        file_response = context.serve(disposition='attachment')
    except FileNotFoundError:
        raise HTTPNotFound()

    return file_response


@view_defaults(
    context=FileEntity
)
class FileCRUD(ContentCRUD):
    """ File CRUD """

    ########
    # POST #
    ########

    @view_config(
        request_method='POST',
        renderer='json',
        context=FolderEntity,
        name='add_file',
        permission='create'
    )
    def post(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(FileSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        data.update({
            'file_size': 0,
            'mime_id': -1,
        })

        new_entity = self.context.create(File, data)

        if new_entity:
            storage_paths = file_utils.get_storage_paths(self.settings,
                                                         new_entity)
            file_utils.save_to_disk(
                self.request, new_entity, data['content'],
                storage_paths['absolute_path']
            )

            self.request.response.status_int = 201
            return schema.dump(new_entity)

        raise HTTPInternalServerError()

    #######
    # PUT #
    #######

    @view_config(
        request_method='PUT',
        renderer='json',
        permission='edit'
    )
    def put(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(FileSchema, exclude={'acls', 'container_id'})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        updated_entity = self.context.update(data)

        if updated_entity:
            evt = FileUpdated(self.request, self.entity)
            self.notify(evt)

            if 'content' in data and data['content'] is not None:
                storage_paths = file_utils.get_storage_paths(self.settings,
                                                         updated_entity)
                file_utils.save_to_disk(
                    self.context, updated_entity, data['content'],
                    storage_paths['absolute_path']
                )

            location = self.request.resource_url(updated_entity)

            return HTTPNoContent(location=location)

        raise HTTPInternalServerError()

    #########################################################################
    # C(R)UD - READ                                                         #
    #########################################################################

    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read'
    )
    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read',
        context=ImageFileEntity,
    )
    def get(self):
        schema = self.schema(FileSchema)
        return schema.dump(self.context.entity, many=False)

    @view_config(
        request_method='GET',
        permission='read',
        context=ImageFileEntity
    )
    def image_get(self):
        if best_match := self.request.accept.best_match(
            self.context.supported_formats.keys()
        ):
            try:
                return self.context.serve(
                    disposition='inline',
                    format=best_match
                )
            except UnsupportedFormatError:
                pass

        raise HTTPNotAcceptable()
