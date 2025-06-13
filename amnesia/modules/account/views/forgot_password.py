from marshmallow import ValidationError

from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.view import view_defaults
from pyramid.view import view_config

from amnesia.utils import recaptcha
from amnesia.utils.forms import render_form

from amnesia.modules.account.validation import ForgotPasswordSchema
from amnesia.modules.account import AuthResource
from amnesia.views import BaseView


def includeme(config):
    config.scan(__name__)


@view_defaults(
    context=AuthResource, 
    name='lost',
    permission='lost',
    renderer='json'
)
class ForgotPassword(BaseView):

    @view_config(request_method='POST')
    def post(self):
        form_data = self.request.POST.mixed()
        schema = self.schema(ForgotPasswordSchema)

        try:
            result = schema.load(form_data)
        except ValidationError as error:
            self.request.response.status_int = 400
            return error.normalized_messages()

        principal = self.context.find_email(result['email'])

        if not principal:
            errors = {'email': "Cannot find specified email in database"}
        elif principal.lost_token:
            errors = {'email': "You have already requested this email. Please check your inbox"}
#        elif not recaptcha.verify(self.request, result['captcha_token']):
#            errors = {'captcha': 'Captcha validation failed'}
        elif self.context.send_token(principal):
            self.request.override_renderer = 'amnesia:templates/account/lost_sent.pt'
            return {'principal': principal}

        if errors:
            return {'form': self.form(form_data, errors)}

        raise HTTPInternalServerError()

