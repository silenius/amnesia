# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPUnauthorized

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Role
from amnesia.modules.account import Permission
from amnesia.modules.account import ACL
from amnesia.modules.account import ACLEntity
from amnesia.modules.account import ContentACLEntity
from amnesia.modules.account import ACLResource
from amnesia.modules.account.validation import ACLSchema
from amnesia.modules.account.validation import ContentACLSchema

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
            'extra_cols': (),
            'permissions': permissions
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST',
                 permission='manage_acl',
                 renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['permission_id'])
        self.context.create(permission, data['allow'])

        return data

    #########
    # PATCH #
    #########

    @view_config(request_method='PATCH',
                 permission='manage_acl',
                 renderer='json')
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['permission_id'])

        self.context.update_permission_weight(permission, data['weight'])
        #self.context.update(permission, **data)

        return data

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE',
                 permission='manage_acl', renderer='json')
    def delete(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        self.context.delete_permission(**data)

        return data


@view_defaults(context=ContentACLEntity, name='', permission='manage_acl')
class ContentACLView(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET', accept='text/html',
                 renderer='amnesia:templates/content/permissions.pt')
    def get_html(self):
        content = self.context.content
        all_permissions = self.context.dbsession.query(Permission).\
            order_by(Permission.name)

        return {
            'content': content,
            'permissions': all_permissions
        }

    @view_config(request_method='GET',
                 accept='application/xml',
                 renderer='amnesia:templates/permissions/_browse.xml')
    def get_xml(self):
        self.request.response.content_type='application/xml'

        permissions = self.context.query().order_by(
            ACL.weight.desc()
        )

        return {
            'extra_cols': {'role'},
            'permissions': permissions
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST', renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        permission = self.context.dbsession.query(Permission).get(data['permission_id'])
        role = self.context.dbsession.query(Role).get(data['role_id'])
        self.context.create(role, permission, data['allow'])

        return data

    #########
    # PATCH #
    #########

    @view_config(request_method='PATCH',
                 renderer='json')
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema()

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        if 'inherits_parent_acl' in data:
            if self.request.has_permission('manage_acl'):
                self.context.set_inherits_parent_acl(data['inherits_parent_acl'])
            else:
                raise HTTPUnauthorized()
            return True
        return False

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', renderer='json')
    def delete(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema()

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        deleted = self.context.delete_permission(data['id'])

        return deleted
