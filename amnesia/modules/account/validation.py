# -*- coding: utf-8 -*-

from marshmallow import Schema
from marshmallow import EXCLUDE
from marshmallow import post_load
from marshmallow import ValidationError
from marshmallow.fields import String
from marshmallow.fields import Email

from marshmallow.validate import Length


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


class ForgotPasswordSchema(Schema):
    email = Email(required=True)
    captcha_token = String(required=True, data_key='g-recaptcha-response',
                           validate=[Length(min=1, error='captcha missing')])

    class Meta:
        unknown = EXCLUDE

class RecoverPasswordSchema(AccountSchema):
    token = String(required=True, validate=[Length(equal=32)])
