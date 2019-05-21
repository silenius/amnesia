# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_load
from marshmallow import ValidationError
from marshmallow.fields import String
from marshmallow.fields import Email
from marshmallow.fields import Integer
from marshmallow.fields import Boolean

from marshmallow.validate import Length
from marshmallow.validate import Range


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
    def check_password_repeat(self, data):
        if 'password' and 'password_repeat' in data:
            if data['password'] != data['password_repeat']:
                raise ValidationError("Passwords don't match", 'password')
            else:
                del data['password_repeat']

        return data


class RoleSchema(Schema):
    role = String(required=True, validate=[Length(min=4)])
    description = String()


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


class ACLSchema(Schema):
    id = Integer(validate=Range(min=1))
    permission_id = Integer(validate=Range(min=1))
    weight = Integer(validation=Range(min=1))
    allow = Boolean()

    class Meta:
        unknown = EXCLUDE

class ContentACLSchema(ACLSchema):
    role_id = Integer(validate=Range(min=1))
    weight = Integer(validation=Range(min=1))
    allow = Boolean()

    class Meta:
        unknown = EXCLUDE
