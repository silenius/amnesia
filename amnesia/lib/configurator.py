# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

#from pyramid.traversal import resource_path_tuple
from pyramid.traversal import _join_path_tuple
from pyramid.interfaces import VH_ROOT_KEY
from pyramid.interfaces import IResourceURL
from zope.interface import implementer

log = logging.getLogger(__name__)

FRONTEND_ASSET_CONFIG_KEYS = {
    'name', 'build_script', 'asset_path'
}


def cms_register_frontend_asset(config, asset_name, asset_config):
    registry = config.registry

    if not hasattr(registry, 'cms_frontend_assets'):
        registry.cms_frontend_assets = OrderedDict()

    def register():
        log.info('===>>> Registering frontend asset: {}'.format(asset_name))
        if asset_name not in registry.cms_frontend_assets:
            to_reg_config = {}

            for key in FRONTEND_ASSET_CONFIG_KEYS:
                to_reg_config[key] = asset_config.get(key, None)

            registry.cms_frontend_assets[asset_name] = to_reg_config

    config.action('amnesiacms_frontend_asset={}'.format(asset_name), register)


@implementer(IResourceURL)
class ContentResourceURL(object):
    VH_ROOT_KEY = VH_ROOT_KEY

    def __init__(self, resource, request):
        #physical_path_tuple = resource_path_tuple(resource)
        physical_path_tuple = ('', str(resource.id))
        physical_path = _join_path_tuple(physical_path_tuple)

        if physical_path_tuple != ('',):
            physical_path_tuple = physical_path_tuple + ('',)
            physical_path = physical_path + '/'

        virtual_path = physical_path
        virtual_path_tuple = physical_path_tuple

        environ = request.environ
        vroot_path = environ.get(self.VH_ROOT_KEY)

        # if the physical path starts with the virtual root path, trim it out
        # of the virtual path
        if vroot_path is not None:
            vroot_path = vroot_path.rstrip('/')
            if vroot_path and physical_path.startswith(vroot_path):
                vroot_path_tuple = tuple(vroot_path.split('/'))
                numels = len(vroot_path_tuple)
                virtual_path_tuple = ('',) + physical_path_tuple[numels:]
                virtual_path = physical_path[len(vroot_path) :]

        self.virtual_path = virtual_path  # IResourceURL attr
        self.physical_path = physical_path  # IResourceURL attr
        self.virtual_path_tuple = virtual_path_tuple  # IResourceURL attr (1.5)
        self.physical_path_tuple = (
            physical_path_tuple
        ) # IResourceURL attr (1.5)


def cms_add_entity_resource(config, entity, resource, add_url_adapter=True):
    registry = config.registry

    if not hasattr(registry, 'cms_entity_resources'):
        registry.cms_entity_resources = OrderedDict()

    def register():
        log.info('===>>> Mapping {} to resource {}'.format(entity, resource))
        registry.cms_entity_resources[entity] = resource

        if add_url_adapter:
            config.add_resource_url_adapter(ContentResourceURL, entity)

    config.action('amnesiacms_entity_resource={}'.format(entity), register)


def cms_get_resource(request, entity):
    cfg = request.registry.cms_entity_resources
    return cfg[type(entity)]
