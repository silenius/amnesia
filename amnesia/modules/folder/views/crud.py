import logging

from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.renderers import render_to_response
from pyramid.security import Authenticated
from pyramid.view import view_config

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

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    config.scan(__name__)


class FolderCRUD(ContentCRUD):
    """ Folder CRUD """

    @view_config(
        context=FolderEntity,
        request_method='GET',
        name='edit',
        renderer='amnesia:templates/folder/edit.pt',
        permission='edit'
    )
    def edit(self):
        schema = FolderSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        form = FolderForm(self.request)
        action = self.request.resource_path(self.context)

        return {
            'form': form.render(data),
            'form_action': action
        }

    @view_config(
        request_method='GET',
        name='add_folder',
        renderer='amnesia:templates/folder/edit.pt',
        context=FolderEntity,
        permission='create'
    )
    def new(self):
        data = self.request.GET.mixed()
        form = FolderForm(self.request)
        action = self.request.resource_path(self.context, '@@add_folder')

        return {
            'form': form.render(data),
            'form_action': action
        }

    #########################################################################
    # (C)RUD - CREATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/folder/edit.pt',
        context=FolderEntity,
        name='add_folder',
        permission='create'
    )
    def create(self):
        form_data = self.request.POST.mixed()
        schema = FolderSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            form = FolderForm(self.request)
            form_action = self.request.resource_path(
                self.context, '@@add_folder'
            )

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

        new_entity = self.context.create(Folder, data)

        if new_entity:
            location = self.request.resource_url(new_entity)
            http_code = data['on_success']
            if http_code == 201:
                return HTTPCreated(location=location)
            if http_code == 303:
                return HTTPSeeOther(location=location)

        raise HTTPInternalServerError()

    #########################################################################
    # C(R)UD - READ                                                         #
    #########################################################################
    @view_config(
        context=FolderEntity,
        request_method='GET',
        permission='read',
        accept='application/json',
        renderer='json'
    )
    def read_json(self):
        return FolderSchema().dump(self.entity)

    @view_config(
        context=FolderEntity,
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
        context=FolderEntity,
        permission='edit'
    )
    def update(self):
        form_data = self.request.POST.mixed()
        schema = FolderSchema(
            context={'request': self.request, 'entity': self.context.entity},
            exclude=('container_id', )
        )

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
def delete(context, request):
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
