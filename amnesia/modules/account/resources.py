# -*- coding: utf-8 -*-

# pylint: disable=E1101

import logging
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
from amnesia.modules.account import ACLResource
from amnesia.modules.account import ContentACL
from amnesia.modules.account import GlobalACL
from amnesia.modules.account import AccountRole

from .util import bcrypt_hash_password
from .util import bcrypt_check_password

log = logging.getLogger(__name__)


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

    def __init__(self, request, role):
        super().__init__(request)
        self.role = role

    @property
    def __name__(self):
        return self.role.id

    def __getitem__(self, path):
        if path == 'acls':
            return ACLEntity(self.request, role=self.role)
        if path == 'members' and not self.role.is_virtual():
            return RoleMember(self.request, role=self.role)

        raise KeyError

    def delete(self):
        try:
            self.dbsession.delete(self.role)
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
            Account.account_roles.any(role=self.role)
        ).all()

    def add_member(self, account):
        try:
            account_role = AccountRole(role=self.role, account=account)
            self.role.accounts.append(account_role)
            self.dbsession.flush()
            return account_role
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


###############################################################################
# ACCESS CONTROL LIST (ACL)                                                   #
###############################################################################

class ACLEntity(Resource):
    ''' Manage ACL for a role '''

    __name__ = 'acls'
    __parent__ = RoleEntity

    def __init__(self, request, role):
        super().__init__(request)
        self.role = role

    def query(self):
        return self.dbsession.query(GlobalACL).filter_by(role=self.role)

    def create(self, permission, allow):
        acl = GlobalACL(role=self.role, permission=permission, allow=allow)

        try:
            self.dbsession.add(acl)
            self.dbsession.flush()
            return acl
        except DatabaseError:
            return False

    # XXX: add patch= arg ?
    def update(self, permission, weight, **data):
        query = self.query().filter_by(permission=permission)

        try:
            role_perm = query.with_lockmode('update').one()
            self.update_permission_weight(permission, weight)

            role_perm.feed(**data)

            self.dbsession.add(role_perm)
            self.dbsession.flush()
            return role_perm
        except (NoResultFound, DatabaseError):
            return False

    def delete_permission(self, permission_id, **kwargs):
        query = self.query().filter_by(permission_id=permission_id)

        try:
            # FIXME: .delete()
            role_perm = query.with_lockmode('update').one()
        except NoResultFound:
            return False

        try:
            self.dbsession.delete(role_perm)
            self.dbsession.flush()
        except DatabaseError:
            return False

        return role_perm

    def update_permission_weight(self, permission, weight):
        """ Change the weight of a permission. """
        query = self.query().filter_by(permission=permission)

        try:
            obj = query.enable_eagerloads(False).with_lockmode('update').one()
        except NoResultFound:
            return False

        (min_weight, max_weight) = sorted((weight, obj.weight))

        # Do we move downwards or upwards ?
        if weight - obj.weight > 0:
            operation = operator.sub
            whens = {min_weight: max_weight}
        else:
            operation = operator.add
            whens = {max_weight: min_weight}

        # Select all the rows between the current weight and the new weight

        # Note: The polymorphic identity WHERE criteria is not included for
        # single- or joined- table updates - this must be added manually, even
        # for single table inheritance.

        # See Caveats section at
        # https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.update
        global_resource = self.dbsession.query(ACLResource.id).filter_by(
            name='GLOBAL').subquery()

        filters = sql.and_(
            GlobalACL.weight.between(min_weight, max_weight),
            GlobalACL.resource_id == global_resource.c.id
        )

        # Swap min_weight/max_weight, or increment/decrement by one depending
        # on whether one moves up or down
        weight = sql.case(
            value=GlobalACL.weight, whens=whens,
            else_=operation(GlobalACL.weight, 1)
        )

        bulk_update = self.dbsession.query(GlobalACL).filter(filters)

        try:
            # The UPDATE statement
            updated = bulk_update.update({'weight': weight},
                                         synchronize_session=False)
            self.dbsession.flush()
            return updated
        except DatabaseError:
            return None


class ContentACLEntity(Resource):
    ''' Manage ACL for a Content based entity '''

    __name__ = 'acl'
    __parent__ = Entity

    def __init__(self, request, content):
        super().__init__(request)
        self.content = content

    def query(self):
        return self.dbsession.query(ContentACL).filter_by(content=self.content)

    def create(self, role, permission, allow):
        acl = ContentACL(content=self.content, role=role, permission=permission,
                         allow=allow)
        try:
            self.dbsession.add(acl)
            self.dbsession.flush()
            return acl
        except DatabaseError:
            return False

    def delete_permission(self, role_id, permission_id, **kwargs):
        filters = sql.and_(ContentACL.permission_id == permission_id,
                           ContentACL.role_id == role_id)

        query = self.query().filter(filters)

        try:
            # FIXME: .delete()
            role_perm = query.with_lockmode('update').one()
        except NoResultFound:
            return False

        try:
            self.dbsession.delete(role_perm)
            self.dbsession.flush()
        except DatabaseError:
            return False

        return role_perm

    def update_permission_weight(self, role, permission, weight):
        """ Change the weight of a permission. """
        filters = sql.and_(
            ContentACL.permission == permission,
            ContentACL.role == role
        )

        query = self.query().filter(filters)

        try:
            obj = query.enable_eagerloads(False).with_lockmode('update').one()
        except NoResultFound:
            return False

        (min_weight, max_weight) = sorted((weight, obj.weight))

        # Do we move downwards or upwards ?
        if weight - obj.weight > 0:
            operation = operator.sub
            whens = {min_weight: max_weight}
        else:
            operation = operator.add
            whens = {max_weight: min_weight}

        # Select all the rows between the current weight and the new weight

        # Note: The polymorphic identity WHERE criteria is not included for
        # single- or joined- table updates - this must be added manually, even
        # for single table inheritance.

        # See Caveats section at
        # https://docs.sqlalchemy.org/en/13/orm/query.html#sqlalchemy.orm.query.Query.update
        content_resource = self.dbsession.query(ACLResource.id).filter_by(
            name='CONTENT').subquery()

        filters = sql.and_(
            ContentACL.content == self.content,
            ContentACL.role == role,
            ContentACL.resource_id == content_resource.c.id,
            ContentACL.weight.between(min_weight, max_weight),
        )

        # Swap min_weight/max_weight, or increment/decrement by one depending
        # on whether one moves up or down
        weight = sql.case(
            value=ContentACL.weight, whens=whens,
            else_=operation(ContentACL.weight, 1)
        )

        bulk_update = self.dbsession.query(ContentACL).filter(filters)

        try:
            # The UPDATE statement
            updated = bulk_update.update({'weight': weight},
                                         synchronize_session=False)
            self.dbsession.flush()
            return updated
        except DatabaseError:
            return None


