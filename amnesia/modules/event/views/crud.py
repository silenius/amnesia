# -*- coding: utf-8 -*-

import logging

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPInternalServerError

from sqlalchemy import sql

from amnesia.modules.folder import FolderEntity
from amnesia.modules.event import Event
from amnesia.modules.event import EventEntity
from amnesia.modules.event.validation import EventSchema
from amnesia.modules.content.views import ContentCRUD

log = logging.getLogger(__name__)


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__, categories=('pyramid', 'amnesia'))


@view_defaults(
    context=EventEntity
)
class EventCRUD(ContentCRUD):
    """ Event CRUD """

    ########
    # POST #
    ########

    @view_config(
        request_method='POST',
        renderer='json',
        context=FolderEntity,
        name='add_event',
        permission='create'
    )
    def create(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(EventSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        new_entity = self.context.create(Event, data)

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
    def update(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(EventSchema, exclude={'acls'})

        try:
            data = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        updated_entity = self.context.update(data)

        if not updated_entity:
            raise HTTPInternalServerError()

        location = self.request.resource_url(updated_entity)

        return HTTPNoContent(location=location)

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        renderer='json',
        accept='application/json',
        permission='read',
    )
    def read_json(self):
        return self.schema(EventSchema).dump(self.entity)
