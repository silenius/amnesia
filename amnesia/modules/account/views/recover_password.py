# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils import recaptcha
from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import RecoverPasswordSchema
from amnesia.modules.account import AuthResource
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=AuthResource, name='recover',
               renderer='amnesia:templates/account/recover.pt')
class RecoverPassword(BaseView):

    form_tmpl = 'amnesia:templates/account/_form_recover.pt'

    def form(self, data=None, errors=None):
        return render_form(self.form_tmpl, self.request, data, errors=errors)

    @view_config(request_method='GET')
    def get(self):
        params = self.request.GET.mixed()
        result, errors = RecoverPasswordSchema(only=['token']).load(params)

        if errors or not self.context.find_token(result['token']):
            raise HTTPNotFound()

        form = self.form({'token': result['token']})

        return {'form': form}

    @view_config(request_method='POST')
    def post(self):
        form_data = self.request.POST.mixed()
        result, errors = RecoverPasswordSchema(
            only=['captcha_token', 'token', 'password', 'password_repeat']
        ).load(form_data)

        if errors:
            return {'form': self.form(form_data, errors)}

        principal = self.context.find_token(result['token'])

        if not principal:
            errors = {'token': 'Invalid token'}
        elif not recaptcha.verify(self.request, result['captcha_token']):
            errors = {'captcha': 'Captcha validation failed'}
        elif not self.context.reset_password(principal, result['password']):
            errors = {'password': 'Cannot reset password'}

        if errors:
            return {'form': self.form(form_data, errors)}

        self.request.override_renderer = 'amnesia:templates/account/recover_ok.pt'

        return {'principal': principal}
