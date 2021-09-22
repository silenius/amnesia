# -*- coding: utf-8 -*-

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.httpexceptions import HTTPInternalServerError

from sqlalchemy import sql

from amnesia.modules.country import Country
from amnesia.modules.folder import FolderEntity
from amnesia.modules.event import Event
from amnesia.modules.event import EventEntity
from amnesia.modules.event.validation import EventSchema
from amnesia.modules.event.forms import EventForm
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class EventCRUD(ContentCRUD):
    """ Event CRUD """

    @view_config(request_method='GET', name='edit',
                 renderer='amnesia:templates/event/edit.pt',
                 context=EventEntity,
                 permission='edit')
    def edit(self):
        schema = EventSchema(context={'request': self.request})
        data = schema.dump(self.entity)
        form = EventForm(self.request)
        action = self.request.resource_path(self.context)

        return {
            'form': form.render(data),
            'form_action': action
        }

    @view_config(request_method='GET', name='add_event',
                 renderer='amnesia:templates/event/edit.pt',
                 context=FolderEntity,
                 permission='create')
    def new(self):
        data = self.request.GET.mixed()
        form = EventForm(self.request)
        action = self.request.resource_path(self.context, '@@add_event')

        return {
            'form': form.render(data),
            'form_action': action
        }

    #########################################################################
    # (C)RUD - CREATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/event/edit.pt',
        context=FolderEntity,
        name='add_event',
        permission='create'
    )
    def create(self):
        form_data = self.request.POST.mixed()
        schema = EventSchema(context={'request': self.request})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            form = EventForm(self.request)
            form_action = self.request.resource_path(
                self.context, '@@add_event'
            )

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

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
    # C(R)UD - READ                                                         #
    #########################################################################

    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read',
        context=EventEntity
    )
    def read_json(self):
        schema = EventSchema(context={'request': self.request})
        return schema.dump(self.context.entity, many=False)

    @view_config(
        request_method='GET',
        renderer='amnesia:templates/event/show.pt',
        accept='text/html',
        permission='read',
        context=EventEntity
    )
    def read_html(self):
        return super().read()

    #########################################################################
    # CR(U)D - UPDATE                                                       #
    #########################################################################

    @view_config(
        request_method='POST',
        renderer='amnesia:templates/event/edit.pt',
        context=EventEntity,
        permission='edit'
    )
    def update(self):
        form_data = self.request.POST.mixed()
        schema = EventSchema(
            context={'request': self.request},
            exclude=('container_id', )
        )

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            form = EventForm(self.request)
            form_action = self.request.resource_path(self.context)

            return {
                'form': form.render(form_data, error.messages),
                'form_action': form_action
            }

        updated_entity = self.context.update(data)

        if updated_entity:
            location = self.request.resource_url(updated_entity)
            return HTTPFound(location=location)
