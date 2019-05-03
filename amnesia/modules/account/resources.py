# -*- coding: utf-8 -*-

# pylint: disable=E1101

import os
import operator

from binascii import hexlify

from pyramid.security import DENY_ALL
from pyramid.security import Everyone
from pyramid.security import Allow
from pyramid.settings import asbool
from pyramid.security import ALL_PERMISSIONS

from pyramid_mailer.message import Message

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import DatabaseError
from sqlalchemy import sql

from amnesia.resources import Resource
from amnesia.modules.content import Entity
from amnesia.modules.account import Account
from amnesia.modules.account import Role
from amnesia.modules.account import ACL
from amnesia.modules.account import AccountRole

from .util import bcrypt_hash_password
from .util import bcrypt_check_password


class AuthResource(Resource):

    __name__ = 'auth'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    def __acl__(self):
        yield Allow, 'role:Manager', ALL_PERMISSIONS
        yield Allow, Everyone, 'login'
        yield Allow, Everyone, 'logout'
        yield Allow, Everyone, 'lost'

        if self.registration_enabled:
            yield Allow, Everyone, 'register'

        yield DENY_ALL

    @property
    def registration_enabled(self):
        return asbool(self.settings.get('registration_enabled'))


class DatabaseAuthResource(AuthResource):

    def __getitem__(self, path):
        if path.isdigit():
            account = self.query.get(path)
            if account:
                return AccountEntity(self.request, account)

        raise KeyError

    @property
    def query(self):
        return self.dbsession.query(Account)

    def get_user(self, user_id):
        return self.query.get(user_id)

    def find_login(self, login, **kwargs):
        try:
            return self.query.filter_by(login=login, **kwargs).one()
        except (NoResultFound, MultipleResultsFound):
            return None

        return None

    def find_email(self, email):
        filters = sql.func.lower(email) == sql.func.lower(Account.email)

        try:
            return self.query.filter(filters).one()
        except (NoResultFound, MultipleResultsFound):
            return None

        return None

    def find_token(self, token):
        try:
            return self.query.filter_by(lost_token=token).one()
        except (NoResultFound, MultipleResultsFound):
            return None

    def check_user_password(self, user, password):
        try:
            return bcrypt_check_password(password, user.password)
        except ValueError:
            return False

    def register(self, data):
        new_account = Account(**data)

        try:
            self.dbsession.add(new_account)
            self.dbsession.flush()
            return new_account
        except DatabaseError:
            return False

    def send_token(self, principal):
        principal.lost_token = hexlify(os.urandom(16)).decode('utf-8')

        mailer = self.request.mailer

        body = '''
Hello {last_name} {first_name},

You have recently requested to reset the password for your account.

To reset your password please go to this page {url}
If you did not perform this request, you can safely ignore this email.
Your password will not be changed unless you choose to follow the link above.

If you require assistance or further information, contact us at {contact}.

Best whishes,
The Belgian Biodiversity Platform'''.format(
    last_name=principal.last_name, first_name=principal.first_name,
    url=self.request.resource_url(
        self, 'recover', query={'token': principal.lost_token}
    ),
    contact='contact@biodiversity.be'
)

        message = Message(
            subject='Lost password',
            sender='noreply@biodiversity.be',
            recipients=[principal.email],
            body=body
        )

        try:
            self.dbsession.add(principal)
            self.dbsession.flush()
            mailer.send(message)
            return principal
        except DatabaseError:
            return False

        return False

    def reset_password(self, principal, password):
        principal.password = bcrypt_hash_password(password)
        principal.lost_token = None

        try:
            self.dbsession.add(principal)
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False

        return False


class AccountEntity(Resource):

    __parent__ = DatabaseAuthResource

    def __init__(self, request, entity):
        super().__init__(request)
        self.entity = entity

    @property
    def __name__(self):
        return self.entity.id


###############################################################################
# ROLE                                                                        #
###############################################################################

class RoleResource(Resource):

    __name__ = 'roles'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    def query(self):
        return self.dbsession.query(Role)

    def __getitem__(self, path):
        if path.isdigit():
            entity = self.dbsession.query(Role).get(path)
            if entity:
                return RoleEntity(self.request, entity)

        raise KeyError

    def create(self, name, description):
        role = Role(name=name, description=description)

        try:
            self.dbsession.add(role)
            self.dbsession.flush()
            return role
        except DatabaseError:
            return False


class RoleEntity(Resource):

    __parent__ = RoleResource

    def __init__(self, request, entity):
        super().__init__(request)
        self.entity = entity

    @property
    def __name__(self):
        return self.entity.id

    def __getitem__(self, path):
        if path == 'acls':
            return ACLEntity(self.request, role=self.entity)
        if path == 'members':
            return RoleMember(self.request, role=self.entity)

        raise KeyError

    def delete(self):
        try:
            self.dbsession.delete(self.entity)
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False


class RoleMember(Resource):

    __parent__ = RoleEntity
    __name__ = 'members'

    def __init__(self, request, role):
        super().__init__(request)
        self.role = role

    def __getitem__(self, path):
        if path.isdigit():
            account = self.dbsession.query(Account).get(path)
            if account:
                return RoleMemberEntity(self.request, role=self.role,
                                        account=account, parent=self,
                                        name=account.id)
        raise KeyError

    def query(self):
        return self.dbsession.query(AccountRole).filter(
            AccountRole == self.role)

    def get_members(self):
        return self.dbsession.query(Account).filter(
            Account.roles.any(role=self.role)
        ).all()

    def add_member(self, account):
        try:
            self.role.accounts.append(account)
            self.dbsession.flush()
            return True
        except DatabaseError:
            return False

    def delete(self):
        try:
            deleted = self.query().delete()
            self.dbsession.flush()
            return deleted
        except DatabaseError:
            return False


class RoleMemberEntity(Resource):

    def __init__(self, request, role, account, parent, name):
        super().__init__(request)
        self.role = role
        self.account = account
        self.__parent__ = parent
        self.__name__ = name

    def query(self):
        filters = sql.and_(AccountRole.role == self.role,
                           AccountRole.account == self.account)
        return self.dbsession.query(AccountRole).filter(filters)

    def delete(self):
        try:
            deleted = self.query().delete()
            self.dbsession.flush()
            return deleted
        except DatabaseError:
            return False


class ACLEntity(Resource):
    ''' Manage ACL for a role '''

    __name__ = 'acls'
    __parent__ = RoleEntity

    def __init__(self, request, role):
        super().__init__(request)
        self.role = role

    def query(self):
        return self.dbsession.query(ACL).filter(
            ACL.role == self.role
        )

    def create(self, permission, allow, resource):
        role_perm = ACL(role=self.role, permission=permission, allow=allow,
                        resource=resource)

        try:
            self.dbsession.add(role_perm)
            self.dbsession.flush()
            return role_perm
        except DatabaseError:
            return False

    def update(self, permission, resource, **data):
        filters = sql.and_(ACL.permission == permission,
                           ACL.resource == resource)

        query = self.query()

        try:
            role_perm = query.filter(filters).with_lockmode('update').one()
            if 'weight' in data:
                self.update_permission_weight(
                    permission, resource, data['weight']
                )

            role_perm.feed(**data)

            self.dbsession.add(role_perm)
            self.dbsession.flush()
            return role_perm
        except (NoResultFound, DatabaseError):
            return False

    def delete_permission(self, permission_id, resource_id):
        filters = sql.and_(
            ACL.permission_id == permission_id,
            ACL.resource_id == resource_id
        )

        query = self.query()

        try:
            role_perm = query.filter(filters).with_lockmode('update').one()
        except NoResultFound:
            return False

        try:
            self.dbsession.delete(role_perm)
            self.dbsession.flush()
        except DatabaseError:
            return False

        return role_perm

    def update_permission_weight(self, permission, resource, new_weight):
        """ Change the weight of a permission. """

        filters = sql.and_(
            ACL.permission == permission,
            ACL.resource == resource
        )

        query = self.query()

        try:
            obj = query.enable_eagerloads(False).filter(filters).\
                with_lockmode('update').one()
        except NoResultFound:
            return False

        (min_weight, max_weight) = sorted((new_weight, obj.weight))

        # Do we move downwards or upwards ?
        if new_weight - obj.weight > 0:
            operation = operator.sub
            whens = {min_weight: max_weight}
        else:
            operation = operator.add
            whens = {max_weight: min_weight}

        # Select all the rows between the current weight and the new weight
        filters = sql.and_(
            ACL.resource == resource,
            ACL.weight.between(min_weight, max_weight)
        )

        # Swap min_weight/max_weight, or increment/decrement by one depending
        # on whether one moves up or down
        new_weight = sql.case(
            value=ACL.weight, whens=whens,
            else_=operation(ACL.weight, 1)
        )

        try:
            # The UPDATE statement
            updated = query.enable_eagerloads(False).filter(filters).\
                update({'weight': new_weight}, synchronize_session=False)
            self.dbsession.flush()
            return updated
        except DatabaseError:
            return None
