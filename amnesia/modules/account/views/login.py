# -*- coding: utf-8 -*-

from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import LoginSchema
from amnesia.modules.account import AuthResource
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(context=AuthResource, name='login', permission='login',
               renderer='amnesia:templates/account/login.pt')
class Login(BaseView):

    form_tmpl = 'amnesia:templates/account/_form_login.pt'

    def form(self, data=None, errors=None):
        return render_form(self.form_tmpl, self.request, data, errors=errors)

    @view_config(request_method='GET')
    def get(self):
        return {'form': self.form()}

    @view_config(request_method='POST')
    def post(self):
        try:
            result = LoginSchema().load(self.request.POST.mixed())
        except ValidationError as error:
            return {'form': self.form(result.data, error.messages)}

        login = result.data['login']
        password = result.data['password']

        user = self.context.find_login(login)

        if user:
            if not user.enabled:
                errors = {'login': 'Error: login must be enabled by an administrator'}
            elif self.context.check_user_password(user, password):
                headers = remember(self.request, str(user.id))
                location = self.request.application_url
                return HTTPFound(location=location, headers=headers)
            else:
                errors = {'password': "Password doesn't match"}
        else:
            errors = {'login': 'Login failed'}

        form = self.form(result.data, errors)

        return {'form': form}
