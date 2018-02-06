# -*- coding: utf-8 -*-

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from amnesia.modules.country import Country
from amnesia.modules.event import EventEntity
from amnesia.modules.event import EventResource
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class EventCRUD(ContentCRUD):
    """ Event CRUD """

    form_tmpl = 'amnesia:templates/event/_form.pt'

    @property
    def schema(self):
        return self.context.get_validation_schema()

    def form(self, data, errors=None):
        if 'countries' not in data:
            # pylint: disable=E1101
            q_country = self.dbsession.query(Country)
            data['countries'] = q_country.order_by(Country.name).all()
        return super().form(data, errors)

    def edit_form(self, form_data, errors=None):
        if errors is None:
            errors = {}

        return {
            'form': self.form(form_data, errors),
            'form_action': self.request.resource_path(self.context)
        }

    @view_config(request_method='GET', name='edit',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventEntity,
                 permission='update')
    def edit(self):
        result = self.schema.dump(self.entity)
        return self.edit_form(result.data)

    @view_config(request_method='GET', name='new',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventResource,
                 permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data)

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventResource,
                 permission='create')
    def create(self):
        form_data = self.request.POST.mixed()

        try:
            data = self.schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages)

        new_entity = self.context.create(data)

        if new_entity:
            return HTTPFound(location=self.request.resource_url(new_entity))

        return self.edit_form(form_data)

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventEntity,
                 permission='update')
    def update(self):
        form_data = self.request.POST.mixed()

        try:
            data = self.schema.load(form_data)
        except ValidationError as error:
            return self.edit_form(form_data, error.messages)

        updated_entity = self.context.update(data)

        if updated_entity:
            return HTTPFound(location=self.request.resource_url(updated_entity))
