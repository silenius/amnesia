import logging

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPNoContent
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound

from marshmallow import ValidationError
from sqlalchemy import sql

from amnesia.views import BaseView

from amnesia.modules.account import (
    Account,
    Role,
    DatabaseAuthResource,
    RoleResource,
    RoleEntity,
    RoleMember,
    RoleMemberEntity,
)

from amnesia.modules.account.validation import (
    BrowseAccountSchema,
    AccountSchema,
    BrowseRoleSchema,
    BrowseRoleMembersSchema,
    BrowseRolePermissionsSchema,
    RoleSchema,
    PermissionSchema,
)

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)


##########
# BROWSE #
##########

@view_defaults(context=RoleResource, name='browse', )
class RoleBrowserView(BaseView):

    def browse(self):
        params = self.request.GET.mixed()
        schema = self.schema(BrowseRoleSchema)

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        roles = self.dbsession.execute(
            self.context.query().order_by(
                Role.virtual.desc(),
                Role.locked.desc(),
                Role.name
            ).limit(
                data['limit']
            ).offset(
                data['offset']
            )
        ).scalars().all()

        count = self.context.count()

        return {
            'data': {
                'roles': roles
            },
            'meta': {
                'count': count,
                'limit': data['limit'],
                'offset': data['offset']
            }
        }


    @view_config(
        request_method='GET',
        accept='application/xml',
        renderer='amnesia:templates/role/_browse.xml'
    )
    def browse_xml(self):
        return self.browse()

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json'
    )
    def browse_json(self):
        data = self.browse()
        data['data']['roles'] = [
            RoleSchema().dump(role) for role in data['data']['roles']
        ]

        return data


@view_defaults(
    context=RoleResource, 
    name=''
)
class RolesCRUD(BaseView):

    ########
    # POST #
    ########

    @view_config(
        request_method='POST', 
        permission='create',
        renderer='json'
    )
    def post(self):
        params = self.request.POST.mixed()
        schema = self.schema(RoleSchema)

        try:
            data = schema.load(params)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        role = self.context.create(data)

        if not role:
            raise HTTPInternalServerError()

        location = self.request.resource_url(self.context, role.id)

        return HTTPCreated(location=location)


##############################################################################
### ROLE ENTITY
##############################################################################

@view_defaults(
    context=RoleEntity, 
    name=''
)
class RoleEntityCRUD(BaseView):

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        permission='read',
        accept='application/json',
        renderer='json'
    )
    def get_json(self):
        role = self.context.role
        return RoleSchema().dump(role)

    #######
    # PUT #
    #######

    # TODO: forbid name==system.
    @view_config(
        request_method='PUT',
        permission='manage_roles'
    )
    def put(self):
        params = self.request.POST.mixed()
        schema = self.schema(RoleSchema)

        try:
            data = schema.load(params)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        role = self.context.update(data)

        if not role:
            raise HTTPInternalServerError()

        location = self.request.resource_url(self.context)

        return HTTPNoContent(location=location)

    ##########
    # DELETE #
    ##########

    @view_config(request_method='DELETE', permission='delete')
    def delete(self):
        if self.context.delete():
            return HTTPNoContent()

        raise HTTPInternalServerError()

@view_defaults(
    context=RoleEntity,
)
class RoleEntityPermission(BaseView):

    # TODO
    @view_config(
        request_method='GET',
        accept='application/json',
        name='global-permissions',
        renderer='json'
    )
    def global_permissions(self):
        params = self.request.GET.mixed()
        schema = self.schema(BrowseRolePermissionsSchema)

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        stmt = self.context.get_global_permissions()
        stmt_count  = sql.select(sql.func.count('*')).select_from(stmt)

        count = self.dbsession.execute(stmt_count).scalar()
        permissions = self.dbsession.execute(
            stmt.offset(data['offset']).limit(data['limit'])
        ).all()

        schema = self.schema(PermissionSchema)

        return {
            'meta': {
                'count': count,
                'limit': data['limit'],
                'offset': data['offset']
            },
            'data': [
                schema.dump(permission[0]) | {
                    'acl_id': permission[1],
                    'allow': permission[2],
                    'weight': permission[3]
                } for permission in permissions
            ]
        }


@view_defaults(context=RoleMember)
class RoleMemberView(BaseView):

    #######
    # GET #
    #######

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json'
    )
    def get_json(self):
        members = self.context.get_members()
        return self.schema(AccountSchema).dump(members, many=True)

    @view_config(
        request_method='GET',
        accept='application/json',
        renderer='json',
        name="all"
    )
    def get_all_json(self):
        params = self.request.GET.mixed()
        schema = self.schema(BrowseRoleMembersSchema) 

        try:
            data = schema.load(params)
        except ValidationError as error:
            raise HTTPBadRequest(error.messages)

        stmt = self.context.get_members(only=False)

        count = self.dbsession.execute(
            sql.select(sql.func.count('*')).select_from(stmt)
        ).scalar()

        members = self.dbsession.execute(
            stmt.offset(
                data['offset']
            ).limit(
                data['limit']
            )
        ).all()

        return {
            'meta': {
                'count': count,
                'limit': data['limit'],
                'offset': data['offset']
            }, 
            'data' : [
                self.schema(AccountSchema).dump(member[0]) | { 'member': member[1] }
                for member in members
            ]
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
            account = self.dbsession.get(Account, account_id)

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
