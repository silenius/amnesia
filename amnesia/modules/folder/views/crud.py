import logging

from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPNoContent
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated
from pyramid.view import view_config
from pyramid.view import view_defaults

from sqlalchemy import orm
from sqlalchemy import sql

from amnesia import order

from amnesia.modules.content_type import ContentType
from amnesia.modules.content.validation import IdListSchema
from amnesia.modules.content.views import ContentCRUD
from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.folder.forms import FolderForm
from amnesia.modules.account import ContentACL

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    config.scan(__name__)


@view_defaults(
    context=FolderEntity,
)
class FolderCRUD(ContentCRUD):
    """ Folder CRUD """

    ########
    # POST #
    ########

    @view_config(
        request_method='POST',
        renderer='json',
        name='add_folder',
        permission='create'
    )
    def post(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(FolderSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        new_entity = self.context.create(Folder, data)

        if new_entity:
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
        schema = self.schema(FolderSchema, exclude={'acls'})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        folder = self.context.update(data)

        if folder:
            location = self.request.resource_url(folder)
            return HTTPNoContent(location=location)
       
        raise HTTPInternalServerError()


    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        permission='read',
        accept='application/json',
        renderer='json'
    )
    def read_json(self):
        return self.schema(FolderSchema).dump(self.entity)


# Bulk delete

@view_config(
    request_method='POST',
    context=FolderEntity,
    name='bulk_delete',
    renderer='json'
)
def bulk_delete(context, request):
    can_bulk_delete = request.has_permission('bulk_delete')
    can_bulk_delete_own = request.has_permission('bulk_delete_own')

    if not any((can_bulk_delete, can_bulk_delete_own)):
        raise HTTPForbidden()

    params = request.POST.mixed()
    schema = IdListSchema()

    try:
        results = schema.load(params)
    except ValidationError as error:
        request.response.status_int = 400
        return error.normalized_messages()

    ids = results['ids']

    if can_bulk_delete:
        return context.bulk_delete(ids)

    if can_bulk_delete_own:
        return context.bulk_delete(ids=ids, owner=request.user)

    raise HTTPForbidden()
