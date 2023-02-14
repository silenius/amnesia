# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPNoContent

from marshmallow import ValidationError

from sqlalchemy import sql
from amnesia.modules.account.resources import GlobalACLEntity

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


@view_defaults(
    context=GlobalACLEntity,
    permission='manage_acl',
    name=''
)
class GlobalACLCRUD(BaseView):

    ##########
    # DELETE #
    ##########

    @view_config(
        request_method='DELETE',
        renderer='json'
    )
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()

    #########
    # PATCH #
    #########

    @view_config(
        request_method='PATCH',
        renderer='json'
    )
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        if 'allow' in data:
            self.context.acl.allow = data['allow']
        if 'weight' in data:
            self.context.update_weight(data['weight'])
        
        return True



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
        all_permissions = self.context.get_permissions(
            order_by=Permission.name
        )

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

        acls = self.context.query(order_by=ACL.weight.desc())

        return {
            'extra_cols': (),
            'permissions': acls
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST',
                 permission='manage_acl',
                 renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        new_entity = self.context.create(
            data['permission'], data['allow']
        )

        if new_entity:
            location = self.request.resource_url(self.context, new_entity.id)
            return HTTPCreated(location=location)

        raise HTTPInternalServerError()

    #########
    # PATCH #
    #########

    @view_config(request_method='PATCH',
                 permission='manage_acl',
                 renderer='json')
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        updated = self.context.update_permission_weight(
            data['permission_id'], data['weight']
        )

        return {'updated': updated}

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE',
                 permission='manage_acl', renderer='json')
    def delete(self):
        form_data = self.request.POST.mixed()
        schema = ACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        if self.context.delete_permission(**data):
            return HTTPNoContent()

        raise HTTPInternalServerError()


@view_defaults(context=ContentACLEntity, name='', permission='manage_acl')
class ContentACLView(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET', accept='text/html',
                 renderer='amnesia:templates/content/permissions.pt')
    def get_html(self):
        content = self.context.content
        all_permissions = self.context.get_permissions(
            order_by=Permission.name
        )

        return {
            'content': content,
            'permissions': all_permissions
        }

    @view_config(request_method='GET',
                 accept='application/xml',
                 renderer='amnesia:templates/permissions/_browse.xml')
    def get_xml(self):
        self.request.response.content_type='application/xml'

        acls = self.context.query(order_by=ACL.weight.desc())

        return {
            'extra_cols': {'role'},
            'permissions': acls
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST', renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        new_acl = self.context.create(
            data['role'], data['permission'], data['allow']
        )

        if new_acl:
            location = self.request.resource_url(self.context, new_acl.id)
            return HTTPCreated(location=location)

        raise HTTPInternalServerError()

    #########
    # PATCH #
    #########

    @view_config(request_method='PATCH',
                 renderer='json')
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        # Inhertis parent ACL
        if 'inherits_parent_acl' in data:
            if not self.context.set_inherits_parent_acl(
                    data['inherits_parent_acl']
            ):
                raise HTTPInternalServerError()

        # Change ACL weight
        if all(k in data for k in ('permission', 'role', 'weight')):
            if not self.context.update_permission_weight(
                    role=data['role'], permission=data['permission'],
                    weight=data['weight']
            ):
                raise HTTPInternalServerError()

        return HTTPNoContent()

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', renderer='json')
    def delete(self):
        form_data = self.request.POST.mixed()
        schema = ContentACLSchema(context={
            'request': self.request
        })

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        deleted = self.context.delete_permission(data['id'])

        return deleted
