# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPNotFound

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Account
from amnesia.modules.account import Role
from amnesia.modules.account import DatabaseAuthResource
from amnesia.modules.account import RoleResource
from amnesia.modules.account import RoleEntity
from amnesia.modules.account import RoleMember
from amnesia.modules.account import RoleMemberEntity
from amnesia.modules.account.validation import BrowseAccountSchema
from amnesia.modules.account.validation import BrowseRoleSchema
from amnesia.modules.account.validation import RoleSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


##########
# BROWSE #
##########

@view_defaults(context=RoleResource, name='browse', permission='browse')
class RoleBrowserView(BaseView):

    @view_config(request_method='GET', accept='application/xml',
                 renderer='amnesia:templates/role/_browse.xml')
    def browse_xml(self):
        params = self.request.GET.mixed()
        schema = BrowseRoleSchema(context={'request': self.request})

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        query = self.context.query()
        count = query.count()
        result = query.order_by(Role.locked.desc()).\
            limit(data['limit']).offset(data['offset']).all()

        return {
            'roles': result,
            'count': count,
            'limit': data['limit'],
            'offset': data['offset']
        }


@view_defaults(context=RoleResource, name='')
class RolesCRUD(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET', accept='text/html',
                 renderer='amnesia:templates/role/browse.pt')
    def get_html(self):
        return {}

    ########
    # POST #
    ########

    @view_config(request_method='POST', permission='create')
    def post(self):
        params = self.request.POST.mixed()
        schema = RoleSchema()

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        role = self.context.create(name=data['role'],
                                   description=data['description'])

        if not role:
            raise HTTPInternalServerError()

        location = self.request.resource_url(self.context, role.id)

        return HTTPCreated(location=location)


@view_config(context=RoleResource, request_method='GET', name='new',
             accept='text/html', renderer='amnesia:templates/role/new.pt',
             permission='create')
def new(context, request):
    return {}


@view_defaults(context=RoleEntity, name='')
class RoleEntityCRUD(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET', permission='read', accept='text/html',
                 renderer='amnesia:templates/role/show.pt')
    def get(self):
        role = self.context.role

        return {
            'role': role
        }

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()


@view_defaults(context=RoleMember)
class RoleMemberView(BaseView):

    #######
    # GET #
    #######

    @view_config(request_method='GET', accept='text/html',
                 renderer='amnesia:templates/role/members.pt')
    def get_html(self):
        accounts = self.context.dbsession.query(Account).all()

        return {
            'role': self.context.role,
            'accounts': accounts
        }

    @view_config(request_method='GET', accept='application/xml',
                 renderer='amnesia:templates/role/_members.xml')
    def get_xml(self):
        accounts = self.context.get_members()

        return {
            'role': self.context.role,
            'accounts': accounts
        }

    ########
    # POST #
    ########

    @view_config(request_method='POST', permission='create')
    def post(self):
        try:
            account_id = int(self.request.POST.getone('account_id'))
        except (KeyError, ValueError) as e:
            raise HTTPInternalServerError()
        else:
            account = self.context.dbsession.query(Account).get(account_id)

            if not account:
                raise HTTPNotFound()

            if self.context.add_member(account):
                return HTTPCreated()

            raise HTTPInternalServerError()

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()


@view_defaults(context=RoleMemberEntity)
class RoleMemberEntityView(BaseView):

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()
