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
from amnesia.modules.account import RoleACLResource
from amnesia.modules.account import ContentACLEntity
from amnesia.modules.account import ContentACLResource
from amnesia.modules.account import ACLResource
from amnesia.modules.account.validation import ACLSchema
from amnesia.modules.content.validation.content import ContentACLSchema

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
        schema = self.schema(ACLSchema)

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        if 'allow' in data:
            self.context.acl.allow = data['allow']
        if 'weight' in data:
            self.context.update_weight(data['weight'])

        return True


@view_defaults(context=RoleACLResource, name='')
class ACLView(BaseView):

    ########
    # POST #
    ########

    @view_config(request_method='POST',
                 permission='manage_acl',
                 renderer='json')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(ACLSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        new_entity = self.context.create(**data)

        if new_entity:
            location = self.request.resource_url(self.context, new_entity.id)
            return HTTPCreated(location=location)

        raise HTTPInternalServerError()

    #########
    # PATCH #
    #########

    @view_config(
        request_method='PATCH',
        permission='manage_acl',
        renderer='json'
    )
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



@view_defaults(
    context=ContentACLResource, 
    name='', 
    permission='manage_acl'
)
class ContentACLView(BaseView):

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json'
    )
    def get_json(self):
        schema = self.schema(ContentACLSchema)

        q = self.context.query().order_by(
            ACL.weight.desc()
        )

        acls = self.dbsession.execute(q).scalars().all()

        return schema.dump(acls, many=True)

    ########
    # POST #
    ########

    @view_config(
        request_method='POST',
        renderer='json'
    )
    def post(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(ContentACLSchema)

        try:
            data = schema.load(form_data)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        new_acl = self.context.create(data)

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
        schema = self.schema(ContentACLSchema)

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
        if all(k in data for k in ('permission_id', 'role_id', 'weight')):
            if not self.context.update_permission_weight(
                    role=data['role'], permission=data['permission'],
                    weight=data['weight']
            ):
                raise HTTPInternalServerError()

        return HTTPNoContent()


@view_defaults(
    context=ContentACLEntity,
    permission='manage_acl',
    name=''
)
class ContentACLCRUD(BaseView):
    
    ##########
    # DELETE #
    ##########

    @view_config(
        request_method='DELETE', 
        renderer='json'
    )
    def delete(self):
        return self.context.delete()


    #########
    # PATCH #
    #########

    @view_config(
        request_method='PATCH',
        renderer='json'
    )
    def patch(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(ACLSchema, only=('allow', 'weight'))

        try:
            data = schema.load(form_data, partial=True)
        except ValidationError as errors:
            raise HTTPBadRequest('Validation error')

        if 'allow' in data:
            self.context.acl.allow = data['allow']
        if 'weight' in data:
            self.context.update_weight(data['weight'])

        return True


