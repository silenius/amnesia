# -*- coding: utf-8 -*-

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPInternalServerError

from amnesia.modules.country import Country
from amnesia.modules.folder import FolderEntity
from amnesia.modules.event import Event
from amnesia.modules.event import EventEntity
from amnesia.modules.event.validation import EventSchema
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class EventCRUD(ContentCRUD):
    """ Event CRUD """

    form_tmpl = 'amnesia:templates/event/_form.pt'

    def form(self, data, errors=None):
        if 'countries' not in data:
            # pylint: disable=E1101
            q_country = self.dbsession.query(Country)
            data['countries'] = q_country.order_by(Country.name).all()
        return super().form(data, errors)

    @view_config(request_method='GET', name='edit',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventEntity,
                 permission='edit')
    def edit(self):
        schema = EventSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        return self.edit_form(data)

    @view_config(request_method='GET', name='add_event',
                 renderer='amnesia:templates/event/edit.pt',
                 context=FolderEntity,
                 permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data, view='@@add_event')

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/event/edit.pt',
                 context=FolderEntity,
                 name='add_event',
                 permission='create')
    def create(self):
        form_data = self.request.POST.mixed()
        schema = EventSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return self.edit_form(form_data, error.messages,
                                  view='@@add_event')

        new_entity = self.context.create(Event, data)

        if new_entity:
            location = self.request.resource_url(new_entity)
            http_code = data['on_success']
            if http_code == 201:
                return HTTPCreated(location=location)
            if http_code == 303:
                return HTTPSeeOther(location=location)

        raise HTTPInternalServerError()

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(request_method='GET', renderer='json',
                 accept='application/json', permission='read',
                 context=EventEntity)
    def read_json(self):
        schema = EventSchema(context={'request': self.request})
        return schema.dump(self.context.entity, many=False)

    @view_config(request_method='GET',
                 renderer='amnesia:templates/event/show.pt',
                 accept='text/html', permission='read',
                 context=EventEntity)
    def read_html(self):
        return super().read()

    #########################################################################
    # UPDATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventEntity,
                 permission='edit')
    def update(self):
        form_data = self.request.POST.mixed()
        schema = EventSchema(
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
