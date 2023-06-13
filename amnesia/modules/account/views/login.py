from marshmallow import ValidationError
from marshmallow import EXCLUDE

from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import LoginSchema
from amnesia.modules.account.validation import AccountSchema
from amnesia.modules.account import AuthResource
from amnesia.modules.account.events import LoginAttemptEvent
from amnesia.modules.account.events import LoginFailureEvent
from amnesia.modules.account.events import LoginSuccessEvent

from ..exc import TooManyAuthenticationFailure

from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(
    context=AuthResource, 
    name='login', 
    permission='login',
    renderer='json'
)
class Login(BaseView):

    @view_config(request_method='POST')
    def post(self):
        params = self.request.POST.mixed()
        schema = self.schema(LoginSchema, unknown=EXCLUDE)

        try:
            data = schema.load(params)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        login = data['login']
        password = data['password']

        user = self.context.find_login(login)

        if user:
            try:
                self.notify(LoginAttemptEvent(user, self.request))
            except TooManyAuthenticationFailure:
                errors = {'login': 'Account is blocked, too many authentication failures.'}
            else:
                if not user.enabled:
                    errors = {'login': 'Error: login must be enabled by an administrator'}
                elif self.context.check_user_password(user, password):
                    data = self.schema(AccountSchema).dump(user)
                    headers = remember(self.request, str(user.id))
                    self.request.response.headers.update(headers)
                    self.notify(LoginSuccessEvent(user, self.request))
                    return data
                else:
                    self.notify(LoginFailureEvent(user, self.request))
                    errors = {'password': "Password doesn't match"}
        else:
            errors = {'login': 'Login failed (unknown user)'}

        self.request.response.status_int = 400
        
        return errors
