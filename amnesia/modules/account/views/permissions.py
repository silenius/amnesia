# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Role
from amnesia.modules.account import Permission
from amnesia.modules.account import ACL
from amnesia.modules.account import ACLEntity
from amnesia.modules.account import ACLResource
from amnesia.modules.account.validation import ACLSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_defaults(context=ACLEntity, name='')
class ACLView(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET',
                 permission='list_permissions',
                 accept='text/html',
                 renderer='amnesia:templates/role/permissions.pt')
    def get_html(self):
        role = self.context.role
        all_permissions = self.context.dbsession.query(Permission).\
            order_by(Permission.name)

        return {
            'role': role,
            'permissions': all_permissions
        }

    @view_config(request_method='GET',
                 permission='list_permissions',
                 accept='application/xml',
                 renderer='amnesia:templates/permissions/_browse.xml')
    def get_xml(self):
        self.request.response.content_type='application/xml'

        permissions = self.context.query().order_by(
            ACL.weight.desc()
        )

        return {
            'permissions': permissions
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST',
                 permission='manage_permission',
                 renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['permission_id'])
        # FIXME
        resource = self.context.dbsession.query(ACLResource).filter_by(name='GLOBAL').one()
        self.context.create(permission, data['allow'], resource=resource)

        return data

    #########
    # PATCH #
    #########

    @view_config(request_method='PATCH',
                 permission='manage_permission',
                 renderer='json')
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['permission_id'])
        # FIXME
        resource = self.context.dbsession.query(ACLResource).filter_by(name='GLOBAL').one()

        self.context.update(permission, resource, **data)

        return data

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE',
                 permission='manage_permission', renderer='json')
    def delete(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        self.context.delete_permission(**data)

        return data
