# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound

from sqlalchemy import orm

from amnesia import order

from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder import FolderResource
from amnesia.modules.folder.validation import FolderSchema
from amnesia.modules.content.views import ContentCRUD
from amnesia.modules.content_type import ContentType

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    config.scan(__name__)


class FolderCRUD(ContentCRUD):
    """ Folder CRUD """

    form_tmpl = 'amnesia:templates/folder/_form.pt'

    def form(self, data=None, errors=None):
        if data is None:
            data = {}

        if 'polymorphic_children_ids' not in data:
            pc_ids = [i['id'] for i in data.get('polymorphic_children', ())]
            data['polymorphic_children_ids'] = pc_ids

        if 'default_order' not in data:
            data['default_order'] = []

        return super().form(data, errors)

    @view_config(context=FolderEntity, request_method='GET', name='edit',
                 renderer='amnesia:templates/folder/edit.pt', permission='edit')
    def edit(self):
        schema = FolderSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        return self.edit_form(data)

    @view_config(request_method='GET', name='add_folder',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderEntity, permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data, view='@@add_folder')

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderEntity,
                 name='add_folder',
                 permission='create')
    def create(self):
        form_data = self.request.POST.mixed()
        schema = FolderSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages,
                                  view='@@add_folder')

        new_entity = self.context.create(Folder, data)

        if new_entity:
            return HTTPFound(location=self.request.resource_url(new_entity))

        return self.edit_form(form_data, view='@@add_folder')

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(context=FolderEntity, request_method='GET', permission='read',
                 accept='text/html')
    def read(self):
        pl_cfg = self.entity.polymorphic_config
        entity = orm.with_polymorphic(pl_cfg.base_mapper.entity, pl_cfg.cls)
        orders = self.request.registry.settings['amnesia:orders']
        all_orders = order.for_entity(entity, orders)

        context = {
            'content': self.entity,
            'orders': all_orders,
        }

        if self.request.has_permission('create'):
            context['content_types'] = self.dbsession.query(ContentType).all()

        try:
            template = self.entity.props['template_show']
        except (TypeError, KeyError):
            template = 'amnesia:templates/folder/show/default.pt'

        try:
            return render_to_response(template, context, request=self.request)
        except (FileNotFoundError, ValueError):
            raise HTTPNotFound()

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderEntity,
                 permission='edit')
    def update(self):
        form_data = self.request.POST.mixed()
        schema = FolderSchema(
            context={'request': self.request},
            exclude=('container_id', )
        )

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages)

        updated_entity = self.context.update(data)

        if updated_entity:
            return HTTPFound(location=self.request.resource_url(updated_entity))
