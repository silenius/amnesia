# -*- coding: utf-8 -*-

import logging

from pkg_resources import iter_entry_points
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.settings import asbool

from amnesia.resources import get_root

log = logging.getLogger(__name__)  # pylint: disable=C0103


def include_pyramid_addons(config):
    config.include('pyramid_chameleon')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_mailer')


def include_authentication(config):
    settings = config.registry.settings
    debug = asbool(settings.get('auth.debug', 'false'))
    http_only = asbool(settings.get('auth.http_only', 'true'))
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'], debug=debug, http_only=http_only
    )
    config.set_authentication_policy(authn_policy)


def include_authorization(config):
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)


def include_security(config):
    config.set_default_csrf_options(require_csrf=True)


def include_entry_points(config):
    for entry_point in iter_entry_points(group='amnesiacms.pkgs'):
        plugin = entry_point.load()
        plugin.includeme(config)


def include_amnesia(config):
    config.include(include_pyramid_addons)
    config.include(include_authentication)
    config.include(include_authorization)
    config.include(include_security)

    config.include('amnesia.subscribers')
    config.include('amnesia.renderers')
    config.include('amnesia.db')

    config.include('amnesia.modules.folder')
    config.include('amnesia.modules.document')
    config.include('amnesia.modules.event')
    config.include('amnesia.modules.account')
    config.include('amnesia.modules.tag')
    config.include('amnesia.modules.state')
    config.include('amnesia.modules.file')
    config.include('amnesia.modules.search')

    config.include('amnesia.modules.content.views')
    config.include('amnesia.views')
    config.include('amnesia.widgets')

    config.include(include_entry_points)

    config.add_static_view(name='static', path='amnesia:static/')

    config.add_resource_url_adapter(entity_resource_adapter)

    #config.scan()
    #config.add_renderer('.html', 'pyramid_chameleon.zpt.renderer_factory')
    config.add_renderer('.xml', 'pyramid_chameleon.zpt.renderer_factory')


def includeme(config):
    config.include(include_amnesia)


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings, root_factory=get_root)
    config.include(include_amnesia)

    return config.make_wsgi_app()


# XXX
from amnesia.modules.folder import Folder
from amnesia.modules.folder import FolderEntity
from amnesia.modules.document import Document
from amnesia.modules.document import DocumentEntity
from amnesia.modules.event import Event
from amnesia.modules.event import EventEntity
from amnesia.modules.file import File
from amnesia.modules.file import FileEntity
from pyramid.traversal import ResourceURL

def entity_resource_adapter(resource, request):
    if isinstance(resource, Folder):
        resource = FolderEntity(request, resource)
    elif isinstance(resource, Document):
        resource = DocumentEntity(request, resource)
    elif isinstance(resource, Event):
        resource = EventEntity(request, resource)
    elif isinstance(resource, File):
        resource = FileEntity(request, resource)

    return ResourceURL(resource, request)
