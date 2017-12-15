# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging

from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPFound

from sqlalchemy import orm

from amnesia import order

from amnesia.modules.folder import FolderEntity
from amnesia.modules.folder import FolderResource
from amnesia.modules.content.views import ContentCRUD
from amnesia.modules.content_type import ContentType

log = logging.getLogger(__name__)  # pylint: disable=C0103


def includeme(config):
    config.scan(__name__)


class FolderCRUD(ContentCRUD):
    """ Folder CRUD """

    form_tmpl = 'amnesia:templates/folder/_form.pt'

    @property
    def schema(self):
        return self.context.get_validation_schema()

    def edit_form(self, form_data, errors=None):
        if errors is None:
            errors = {}

        return {
            'form': self.form(form_data, errors),
            'form_action': self.request.resource_path(self.context)
        }

    def form(self, data=None, errors=None):
        if data is None:
            data = {}

        if 'polymorphic_children_ids' not in data:
            pc_ids = [i['id'] for i in data.get('polymorphic_children', ())]
            data['polymorphic_children_ids'] = pc_ids

        if 'default_order' not in data:
            data['default_order'] = []

        return super().form(data, errors)

    @view_config(context=FolderEntity,
                 request_method='GET',
                 name='edit',
                 renderer='amnesia:templates/folder/edit.pt',
                 permission='update')
    def edit(self):
        result = self.schema.dump(self.entity)
        return self.edit_form(result.data)

    @view_config(request_method='GET', name='new',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderResource,
                 permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data)

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderResource, permission='create')
    def create(self):
        form_data = self.request.POST.mixed()
        data, errors = self.schema.load(form_data)

        if errors:
            return self.edit_form(form_data, errors)

        new_entity = self.context.create(data)

        if new_entity:
            return HTTPFound(location=self.request.resource_url(new_entity))

        return self.edit_form(form_data)

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

        return render_to_response(template, context, request=self.request)

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/folder/edit.pt',
                 context=FolderEntity,
                 permission='update')
    def update(self):
        form_data = self.request.POST.mixed()
        data, errors = self.schema.load(form_data)

        if errors:
            return self.edit_form(form_data, errors)

        updated_entity = self.context.update(data)

        if updated_entity:
            return HTTPFound(location=self.request.resource_url(updated_entity))
