# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.httpexceptions import HTTPBadRequest
from pyramid_mailer.message import Message

from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow.fields import String
from marshmallow.fields import Email
from marshmallow.validate import Length

from amnesia.utils import recaptcha


def includeme(config):
    config.scan(__name__)


class NewsLetter(Schema):
    name = String(required=True)
    email = Email(required=True)
    captcha_token = String(
        required=True, load_from='g-recaptcha-response',
        validate=[Length(min=1, error='captcha missing')]
    )


@view_config(name='newsletter', request_method='POST',
             renderer='json')
def newsletter(request):
    recipients = request.registry.settings['contact_recipients'].split(',')

    try:
        data = NewsLetter().load(request.POST.mixed())
    except ValidationError as error:
        raise HTTPBadRequest(error.messages)

    if recaptcha.verify(request, data['captcha_token']):
        mailer = request.mailer

        message = '''
Hello,

{} wants to subscribe to the newsletter with the following address: {}
'''.format(data['name'], data['email'])

        message = Message(
            subject='Newsflash subscription',
            sender=data['email'],
            recipients=recipients,
            body=message
        )

        mailer.send_immediately(message, fail_silently=False)

        return data

    raise HTTPInternalServerError()

