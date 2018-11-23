# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

from pyramid.traversal import ResourceURL

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


def cms_add_entity_resource(config, entity, resource, add_url_adapter=True):
    registry = config.registry

    if not hasattr(registry, 'cms_entity_resources'):
        registry.cms_entity_resources = OrderedDict()

    def register():
        log.info('===>>> Mapping {} to resource {}'.format(entity, resource))
        registry.cms_entity_resources[entity] = resource

        if add_url_adapter:
            config.add_resource_url_adapter(
                lambda resource2, request:
                ResourceURL(resource(request, resource2), request),
                entity)

    config.action('amnesiacms_entity_resource={}'.format(entity), register)


def cms_get_resource(request, entity):
    cfg = request.registry['cms_entity_resources']
    return cfg[type(entity)]
