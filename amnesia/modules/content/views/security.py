import logging

from pyramid.view import view_config

from amnesia.modules.content import Entity
from amnesia.modules.account.security import get_parent_acl

log = logging.getLogger(__name__)


def includeme(config):
    config.scan(__name__)

@view_config(
    name='acls',
    context=Entity,
    renderer='json'
)
def acls(context, request):

    return get_parent_acl(context)
