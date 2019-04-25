# -*- coding: utf-8 -*-

import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest

from sqlalchemy import sql

from marshmallow import ValidationError

from amnesia.views import BaseView
from amnesia.modules.account import Account
from amnesia.modules.account import Role
from amnesia.modules.account import DatabaseAuthResource
from amnesia.modules.account import RoleResource
from amnesia.modules.account import RoleEntity
from amnesia.modules.account.validation import BrowseAccountSchema
from amnesia.modules.account.validation import BrowseRoleSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_defaults(context=DatabaseAuthResource, permission='browse')
class AccountBrowserView(BaseView):

    @view_config(request_method='GET', name='browse', accept='application/xml',
                 renderer='amnesia:templates/account/_browse.xml')
    def browse_xml(self):
        params = self.request.GET.mixed()
        schema = BrowseAccountSchema(context={'request': self.request})

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        query = self.context.query
        count = query.count()
        result = query.order_by(sql.func.lower(Account.login)).\
            limit(data['limit']).offset(data['offset']).all()

        return {
            'accounts': result,
            'count': count,
            'limit': data['limit'],
            'offset': data['offset']
        }

    @view_config(request_method='GET', name='', accept='text/html',
                 renderer='amnesia:templates/account/browse.pt')
    def index(self):
        return {}


@view_defaults(context=RoleResource, permission='browse')
class RoleBrowserView(BaseView):

    @view_config(request_method='GET', name='browse', accept='application/xml',
                 renderer='amnesia:templates/role/_browse.xml')
    def browse_xml(self):
        params = self.request.GET.mixed()
        schema = BrowseRoleSchema(context={'request': self.request})

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        query = self.context.query
        count = query.count()
        result = query.order_by(Role.locked.desc()).\
            limit(data['limit']).offset(data['offset']).all()

        return {
            'roles': result,
            'count': count,
            'limit': data['limit'],
            'offset': data['offset']
        }

    @view_config(request_method='GET', name='', accept='text/html',
                 renderer='amnesia:templates/role/browse.pt')
    def index(self):
        return {}
