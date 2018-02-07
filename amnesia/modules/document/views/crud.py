# -*- coding: utf-8 -*-

from marshmallow import ValidationError

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from amnesia.modules.document import DocumentEntity
from amnesia.modules.document import DocumentResource

from ...content.views import ContentCRUD

def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)


class DocumentCRUD(ContentCRUD):
    ''' Document CRUD '''

    form_tmpl = 'amnesia:templates/document/_form.pt'

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

    @view_config(request_method='GET', name='edit',
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentEntity,
                 permission='update')
    def edit(self):
        data = self.schema.dump(self.entity)
        return self.edit_form(data)

    @view_config(request_method='GET', name='new',
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentResource,
                 permission='create')
    def new(self):
        form_data = self.request.GET.mixed()
        return self.edit_form(form_data)

    #########################################################################
    # READ                                                                  #
    #########################################################################

    @view_config(request_method='GET', renderer='json',
                 accept='application/json', permission='read',
                 context=DocumentEntity)
    def read_json(self):
        schema = self.context.get_validation_schema()
        return schema.dump(self.context.entity, many=False).data

    @view_config(request_method='GET',
                 accept='text/html', permission='read',
                 context=DocumentEntity)
    def read_html(self):
        return super().read()

    #########################################################################
    # CREATE                                                                #
    #########################################################################

    @view_config(request_method='POST',
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentResource,
                 permission='create')
    def create(self):
        ''' Create a new Document '''
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
                 renderer='amnesia:templates/document/edit.pt',
                 context=DocumentEntity,
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
