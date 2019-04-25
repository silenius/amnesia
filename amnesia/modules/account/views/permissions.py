# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Role
from amnesia.modules.account import Permission
from amnesia.modules.account import RoleEntity
from amnesia.modules.account import Policy
from amnesia.modules.account.validation import RolePermissionSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_defaults(context=RoleEntity)
class RolePermission(BaseView):

    @view_config(request_method='GET', name='permissions',
                 permission='list_permissions',
                 accept='text/html',
                 renderer='amnesia:templates/role/permissions.pt')
    def permissions_get_html(self):
        role = self.context.entity
        all_permissions = self.context.dbsession.query(Permission).\
            order_by(Permission.name)

        return {
            'role': role,
            'permissions': all_permissions
        }

    @view_config(request_method='GET', name='permissions',
                 permission='list_permissions',
                 accept='application/xml',
                 renderer='amnesia:templates/permissions/_browse.xml')
    def permissions_get_xml(self):
        role = self.context.entity
        self.request.response.content_type='application/xml'

        return {
            'role': role
        }

    @view_config(request_method='POST', name='permissions',
                 permission='change_permissions',
                 renderer='json')
    def permissions_post(self):
        form_data = self.request.POST.mixed()
        schema = RolePermissionSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['perm_id'])
        # FIXME
        policy = self.context.dbsession.query(Policy).filter_by(name='GLOBAL').one()
        self.context.set_permission(permission, data['allow'], policy=policy)

        return data

    @view_config(request_method='DELETE', name='permissions',
                 permission='delete_permission', renderer='json')
    def permission_delete(self):
        form_data = self.request.POST.mixed()
        schema = RolePermissionSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        self.context.delete_permission(**data)

        return data
