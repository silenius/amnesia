import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.folder import FolderEntity
from amnesia.modules.file import File
from amnesia.modules.file import utils as file_utils
from amnesia.modules.file import FileEntity
from amnesia.modules.file import ImageFileEntity
from amnesia.modules.file.validation import FileSchema
from amnesia.modules.file.events import FileUpdated
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
def download(context, request):
    try:
        file_response = context.serve()
    except FileNotFoundError:
        raise HTTPNotFound()

    return file_response


@view_config(
    context=ImageFileEntity,
    name='download',
    request_method='GET',
    permission='read',
    renderer='string'
)
def image_download(context, request):
    return request.accept.best_match((
        'imagee/lol', 'imagee/bar'
    ), "image/webp")




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
            'original_name': ''
        })

        new_entity = self.context.create(File, data)

        if new_entity:
            file_utils.save_to_disk(self.request, new_entity, data['content'])
            self.request.response.status_int = 201
            return schema.dump(new_entity)

        raise HTTPInternalServerError()

    #######
    # PUT #
    #######

    @view_config(
        request_method='PUT',
        renderer='json',
        context=FileEntity,
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

            if data.get('content'):
                file_utils.save_to_disk(
                    self.request, updated_entity, data['content']
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
        permission='read',
        context=FileEntity
    )
    def get(self):
        schema = self.schema(FileSchema)
        return schema.dump(self.context.entity, many=False)
