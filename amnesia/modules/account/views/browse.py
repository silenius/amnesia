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
from amnesia.modules.account.validation import BrowseAccountSchema
from amnesia.modules.account.validation import BrowseRoleSchema
from amnesia.modules.account.validation import AccountSchema

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


@view_defaults(context=DatabaseAuthResource)
class AccountBrowserView(BaseView):

    def browse(self):
        params = self.request.GET.mixed()
        schema = self.schema(BrowseAccountSchema)

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        count = self.context.count()
        result = self.dbsession.execute(
            self.context.query().order_by(
                sql.func.lower(Account.login)
            ).limit(
                data['limit']
            ).offset(
                data['offset']
            )
        ).scalars().all()

        return {
            'accounts': result,
            'count': count,
            'limit': data['limit'],
            'offset': data['offset']
        }

    @view_config(
        request_method='GET', 
        name='browse', 
        accept='application/json',
        renderer='json'
    )
    def browse_json(self):
        data = self.browse()
        
        return {
            'data': {
                'accounts': self.schema(AccountSchema).dump(
                    data['accounts'],
                    many=True
                )
            },
            'meta': {
                'count': data['count'],
                'limit': data['limit'],
                'offset': data['offset']
            }
        }
 
    @view_config(request_method='GET', name='browse', accept='application/xml',
                 renderer='amnesia:templates/account/_browse.xml')
    def browse_xml(self):
        return self.browse()

    @view_config(request_method='GET', name='', accept='text/html',
                 renderer='amnesia:templates/account/browse.pt')
    def index(self):
        return {}
