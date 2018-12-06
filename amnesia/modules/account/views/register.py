# -*- coding: utf-8 -*-

from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils import recaptcha
from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import AccountSchema
from amnesia.modules.account import AuthResource
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=AuthResource, name='register', permission='register',
               renderer='amnesia:templates/account/register.pt')
class Register(BaseView):

    form_tmpl = 'amnesia:templates/account/_form_register.pt'

    def form(self, data=None, errors=None):
        return render_form(self.form_tmpl, self.request, data, errors=errors)

    @view_config(request_method='GET')
    def get(self):
        return {'form': self.form()}

    @view_config(request_method='POST')
    def post(self):
        form_data = self.request.POST.mixed()

        try:
            result = AccountSchema().load(form_data)
        except ValidationError as error:
            return {'form': self.form(form_data, error.messages)}

        if self.context.find_login(result['login']):
            errors = {'login': 'Login already exist'}
        elif not recaptcha.verify(self.request, result['captcha_token']):
            errors = {'captcha': 'Captcha validation failed'}
        else:
            errors = None

        if errors:
            return {'form': self.form(form_data, errors)}

        new_account = self.context.register(result)

        if not new_account:
            raise HTTPInternalServerError()

        self.request.override_renderer = 'amnesia:templates/account/register_ok.pt'

        return {'new_account': new_account}
