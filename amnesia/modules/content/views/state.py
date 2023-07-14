import logging

from pyramid.view import view_config

from amnesia.modules.content import Entity

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)



@view_config(
    name='publish',
    context=Entity,
    request_method='POST',
    renderer='json',
    permission='publish'
)
def publish(context, request):
    ...

@view_config(
    name='unpublish',
    context=Entity,
    request_method='POST',
    renderer='json',
    permission='unpublish'
)

def unpublish(context, request):
    ...
