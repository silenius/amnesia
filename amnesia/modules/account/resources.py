# -*- coding: utf-8 -*-

# pylint: disable=E1101

import os
from binascii import hexlify

from pyramid.security import DENY_ALL
from pyramid.security import Everyone
from pyramid.security import Authenticated
from pyramid.security import Allow
from pyramid.security import Deny
from pyramid.settings import asbool

from pyramid_mailer.message import Message

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.exc import DatabaseError
from sqlalchemy import sql

from amnesia.resources import Resource
from amnesia.modules.account import Account
from .util import bcrypt_hash_password
from .util import bcrypt_check_password


class AuthResource(Resource):

    __name__ = 'auth'

    def __init__(self, request, parent):
        super().__init__(request)
        self.__parent__ = parent

    def __acl__(self):
        yield Deny, Authenticated, 'login'
        yield Allow, Authenticated, 'logout'
        yield Deny, Everyone, 'logout'
        yield Allow, Everyone, 'login'
        yield Allow, Everyone, 'lost'

        if self.registration_enabled:
            yield Allow, Everyone, 'register'

        yield DENY_ALL

    @property
    def registration_enabled(self):
        return asbool(self.settings.get('registration_enabled'))


class DatabaseAuthResource(AuthResource):

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
