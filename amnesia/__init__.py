# -*- coding: utf-8 -*-

from pyramid.config import Configurator
# from pyramid.static import QueryStringConstantCacheBuster
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings

from pyramid.settings import asbool

from amnesia.resources import get_root

def add_pyramid_addons(config):
    config.include('pyramid_chameleon')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_mailer')


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    config = Configurator(settings=settings, root_factory=get_root)

    # Session
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    # Authentication
    authn_policy = AuthTktAuthenticationPolicy(
        settings['auth.secret'],
        debug=asbool(settings.get('auth.debug', 'false'))
    )

    config.set_authentication_policy(authn_policy)

    # Authorization
    authz_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authz_policy)

    #from pyramid.security import DENY_ALL, NO_PERMISSION_REQUIRED
    #config.set_default_permission(NO_PERMISSION_REQUIRED)
    #config.set_default_permission('read')

#    config.set_default_csrf_options(require_csrf=True)

    # Include addons
    config.include(add_pyramid_addons)

    config.include('amnesia.renderers')
    config.include('amnesia.db')

    config.include('amnesia.modules.event')
    config.include('amnesia.modules.document')
    config.include('amnesia.modules.account')
    config.include('amnesia.modules.tag')
    config.include('amnesia.modules.state')
    config.include('amnesia.modules.folder')
    config.include('amnesia.modules.file')
    config.include('amnesia.modules.search')

    config.include('amnesia.modules.content.views')

    config.add_static_view(name='static', path='amnesia:static/')

    config.add_resource_url_adapter(entity_resource_adapter)

    config.scan()
    #config.add_renderer('.html', 'pyramid_chameleon.zpt.renderer_factory')
    config.add_renderer('.xml', 'pyramid_chameleon.zpt.renderer_factory')

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
from amnesia.modules.tag import Tag
from amnesia.modules.tag import TagEntity
from pyramid.interfaces import IResourceURL
from zope.interface import implementer
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



# XXX: temp ...

from pyramid.events import BeforeRender
from pyramid.events import subscriber
from sqlalchemy import orm

from amnesia import widgets
from saexts import Serializer

from amnesia.utils.text import shorten
from amnesia.utils.text import fmt_datetime
from amnesia.utils.gravatar import gravatar
from amnesia.modules.event.utils import pretty_date
from amnesia.modules.content import Content

def dump_obj(obj, format, **kwargs):
    return getattr(Serializer(obj), format)(**kwargs)

def polymorphic_hierarchy(cls=Content):
    return list(orm.class_mapper(cls).base_mapper.polymorphic_iterator())


@subscriber(BeforeRender)
def globals_factory(event):
    event['h'] = {
        'shorten': shorten,
        'fmt_datetime': fmt_datetime,
        'event_date': pretty_date,
        'gravatar': gravatar,
        'polymorphic_hierarchy': polymorphic_hierarchy,
        'asbool': asbool,
    }

    event['widgets'] = widgets
    event['dump_obj'] = dump_obj
