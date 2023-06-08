from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_load
from marshmallow import post_dump
from marshmallow import ValidationError
from marshmallow.fields import DateTime, String
from marshmallow.fields import Email
from marshmallow.fields import Integer
from marshmallow.fields import Boolean
from marshmallow.fields import Nested

from marshmallow.validate import Length
from marshmallow.validate import Range

from amnesia.utils.gravatar import gravatar
from amnesia.utils.validation import PyramidContextMixin

class LoginSchema(Schema):
    login = String(required=True, validate=Length(min=4))
    password = String(required=True, load_only=True, validate=Length(min=4))


class AccountSchema(Schema):
    id = Integer(dump_only=True)
    login = String(required=True, validate=Length(min=4))
    password = String(required=True, load_only=True, validate=Length(min=4))
    password_repeat = String(required=True, load_only=True,
                             validate=Length(min=4))
    last_name = String(required=True)
    first_name = String(required=True)
    full_name = String(dump_only=True)
    enabled = Boolean()
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

    @post_dump
    def gravatar(self, data, **kwargs):
        data['gravatar'] = gravatar(data['email'])
        return data


class RoleSchema(Schema):
    name = String(required=True, validate=[Length(min=4)])
    description = String()
    id = Integer(dump_only=True)
    created = DateTime(dump_only=True)
    enabled = Boolean(dump_only=True)
    locked = Boolean(dump_only=True)
    virtual = Boolean(dump_only=True)

    class Meta:
        unknown = EXCLUDE

class PermissionSchema(Schema):
    id = Integer(dump_only=True)
    name = String(required=True, validate=[Length(min=4)])
    description = String()
    created = DateTime(dump_only=True)
    enabled = Boolean(dump_only=True)

    class Meta:
        unknown = EXCLUDE


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


class ResourceSchema(Schema):
    id = Integer(validate=Range(min=1), dump_only=True)
    name = String()

class ACLSchema(Schema, PyramidContextMixin):
    id = Integer(validate=Range(min=1), dump_only=True)
    permission = Nested(PermissionSchema, dump_only=True)
    permission_id = Integer(validate=Range(min=1), load_only=True)
    role_id = Integer(load_only=True, validate=Range(min=1))
    role = Nested(RoleSchema, dump_only=True)
    resource = Nested(ResourceSchema, dump_only=True)
    weight = Integer(validation=Range(min=1))
    allow = Boolean()

    class Meta:
        unknown = EXCLUDE
