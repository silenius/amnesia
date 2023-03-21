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
    name=''
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
    def create(self):
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
            raise HTTPBadRequest(error.messages)

        folder = self.context.update(data)

        if not folder:
            raise HTTPInternalServerError()

        location = self.request.resource_url(folder)

        return HTTPNoContent(location=location)



    #########################################################################
    # C(R)UD - READ                                                         #
    #########################################################################

    @view_config(
        request_method='GET',
        permission='read',
        accept='application/json',
        renderer='json'
    )
    def read_json(self):
        return self.schema(FolderSchema).dump(self.entity)

    @view_config(
        request_method='GET',
        permission='read',
        accept='text/html'
    )
    def read(self):
        pl_cfg = self.entity.polymorphic_config
        entity = orm.with_polymorphic(pl_cfg.base_mapper.entity, pl_cfg.cls)
        orders = self.registry.settings['amnesia:orders']
        all_orders = order.for_entity(entity, orders)

        context = {
            'content': self.entity,
            'orders': all_orders,
        }

        if self.request.has_permission('create'):
            stmt = sql.select(ContentType).order_by(ContentType.name)
            result = self.dbsession.execute(stmt).scalars().all()
            context['content_types'] = result

        try:
            template = self.entity.props['template_show']
        except (TypeError, KeyError):
            template = 'amnesia:templates/folder/show/default.pt'

        try:
            return render_to_response(template, context, request=self.request)
        except (FileNotFoundError, ValueError):
            raise HTTPNotFound()

    #########################################################################
    # CR(U)D - UPDATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/folder/edit.pt',
        permission='edit'
    )
    def update(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(exclude={'container_id', 'acls'})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            form = FolderForm(self.request)
            form_action = self.request.resource_path(self.context)

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

        updated_entity = self.context.update(data)

        if updated_entity:
            location = self.request.resource_url(updated_entity)
            return HTTPFound(location=location)

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
        raise HTTPBadRequest(error.messages)

    ids = results['ids']

    if can_bulk_delete:
        return context.bulk_delete(ids)

    if can_bulk_delete_own:
        return context.bulk_delete(ids=ids, owner=request.user)

    raise HTTPForbidden()
