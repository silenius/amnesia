# -*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid_mailer.message import Message

from marshmallow import Schema
from marshmallow.fields import String
from marshmallow.fields import Email
from marshmallow.fields import Integer
from marshmallow.validate import Length

from amnesia.utils import recaptcha
from amnesia.modules.content import Content


def includeme(config):
    config.scan(__name__)


class MessageValidation(Schema):
    user = String()
    email = Email()
    website = String(required=False)
    subject = String()
    message = String()
    oid = Integer()
    captcha_token = String(
        required=True, load_from='g-recaptcha-response',
        validate=[Length(min=1, error='captcha missing')]
    )


@view_config(name='contact', request_method='POST',
             renderer='amnesia:templates/contact/success.pt')
def contact(request):
    recipients = request.registry.settings['contact_recipients'].split(',')
    data, errors = MessageValidation().load(request.POST.mixed())

    if errors:
        raise HTTPInternalServerError()

    if recaptcha.verify(request, data['captcha_token']):
        mailer = request.mailer

        message = data['message']
        message = 'This message has been sent by a visitor of {}:\n\n'.format(
            request.application_url
        ) + message

        message = Message(
            subject=data['subject'],
            sender=data['email'],
            recipients=recipients,
            body=message
        )

        mailer.send_immediately(message, fail_silently=False)

        obj = request.dbsession.query(Content).get(data['oid'])

        return {
            'content': obj,
            'submitted': data
        }

    raise HTTPInternalServerError()


