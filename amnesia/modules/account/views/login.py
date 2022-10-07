from marshmallow import ValidationError
from marshmallow import EXCLUDE

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import LoginSchema
from amnesia.modules.account import AuthResource
from amnesia.modules.account.events import LoginAttemptEvent
from amnesia.modules.account.events import LoginFailureEvent
from amnesia.modules.account.events import LoginSuccessEvent
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
        params = self.request.POST.mixed()
        notify = self.request.registry.notify

        try:
            data = LoginSchema(unknown=EXCLUDE).load(params)
        except ValidationError as error:
            return {'form': self.form(params, error.messages)}

        login = data['login']
        password = data['password']

        user = self.context.find_login(login)

        if user:
            notify(LoginAttemptEvent(user, self.request))

            if not user.enabled:
                errors = {'login': 'Error: login must be enabled by an administrator'}
            elif self.context.check_user_password(user, password):
                headers = remember(self.request, str(user.id))
                location = self.request.application_url
                notify(LoginSuccessEvent(user, self.request))
                return HTTPFound(location=location, headers=headers)
            else:
                notify(LoginFailureEvent(user, self.request))
                errors = {'password': "Password doesn't match"}
        else:
            errors = {'login': 'Login failed (unknown user)'}

        form = self.form(data, errors)

        return {'form': form}
