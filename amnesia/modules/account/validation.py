# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_load
from marshmallow import ValidationError
from marshmallow.fields import DateTime, String
from marshmallow.fields import Email
from marshmallow.fields import Integer
from marshmallow.fields import Boolean

from marshmallow.validate import Length
from marshmallow.validate import Range

from amnesia.modules.account import Role
from amnesia.modules.account import Permission

from amnesia.utils.validation import PyramidContextMixin


class LoginSchema(Schema):
    login = String(required=True, validate=Length(min=4))
    password = String(required=True, load_only=True, validate=Length(min=4))


class AccountSchema(Schema):
    login = String(required=True, validate=Length(min=4))
    password = String(required=True, load_only=True, validate=Length(min=4))
    password_repeat = String(required=True, load_only=True,
                             validate=Length(min=4))
    last_name = String(required=True)
    first_name = String(required=True)
    email = Email(required=True)
    captcha_token = String(required=True, data_key='g-recaptcha-response',
                           validate=[Length(min=1, error='captcha missing')])

    class Meta:
        unknown = EXCLUDE

    @post_load
    def check_password_repeat(self, data, **kwargs):
        if 'password' and 'password_repeat' in data:
            if data['password'] != data['password_repeat']:
                raise ValidationError("Passwords don't match", 'password')
            else:
                del data['password_repeat']

        return data


class RoleSchema(Schema):
    name = String(required=True, validate=[Length(min=4)])
    description = String()
    id = Integer(dump_only=True)
    created = DateTime(dump_only=True)
    enabled = Boolean(dump_only=True)
    locked = Boolean(dump_only=True)
    virtual = Boolean(dump_only=True)


class ForgotPasswordSchema(Schema):
    email = Email(required=True)
    captcha_token = String(required=True, data_key='g-recaptcha-response',
                           validate=[Length(min=1, error='captcha missing')])

    class Meta:
        unknown = EXCLUDE

class RecoverPasswordSchema(AccountSchema):
    token = String(required=True, validate=[Length(equal=32)])


class BrowseAccountSchema(Schema):
    limit = Integer(validate=Range(min=1, max=100), missing=50)
    offset = Integer(validate=Range(min=0), missing=0)

    class Meta:
        unknown = EXCLUDE


class BrowseRoleSchema(Schema):
    limit = Integer(validate=Range(min=1, max=100), missing=50)
    offset = Integer(validate=Range(min=0), missing=0)

    class Meta:
        unknown = EXCLUDE


class ACLSchema(Schema, PyramidContextMixin):
    id = Integer(validate=Range(min=1))
    permission_id = Integer(validate=Range(min=1))
    weight = Integer(validation=Range(min=1))
    allow = Boolean()

    class Meta:
        unknown = EXCLUDE

    @post_load
    def permission(self, item, **kwargs):
        if 'permission_id' in item:
            item['permission'] = self.dbsession.get(
                Permission, item['permission_id']
            )

        return item

class ContentACLSchema(ACLSchema):
    role_id = Integer(validate=Range(min=1))
    weight = Integer(validation=Range(min=1))
    inherits_parent_acl = Boolean()
    allow = Boolean()

    class Meta:
        unknown = EXCLUDE

    @post_load
    def role(self, item, **kwargs):
        if 'role_id' in item:
            item['role'] = self.dbsession.get(Role, item['role_id'])

        return item
