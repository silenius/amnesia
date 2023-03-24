# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

log = logging.getLogger(__name__)

FRONTEND_ASSET_CONFIG_KEYS = {
    'name', 'build_script', 'asset_path'
}


def cms_register_frontend_asset(config, asset_name, asset_config):
    registry = config.registry

    if not hasattr(registry, 'cms_frontend_assets'):
        registry.cms_frontend_assets = OrderedDict()

    def register():
        log.info('===>>> Registering frontend asset: %s', asset_name)
        if asset_name not in registry.cms_frontend_assets:
            to_reg_config = {}

            for key in FRONTEND_ASSET_CONFIG_KEYS:
                to_reg_config[key] = asset_config.get(key, None)

            registry.cms_frontend_assets[asset_name] = to_reg_config

    config.action(f'amnesiacms_frontend_asset={asset_name}', register)


def cms_add_entity_resource(config, entity, resource):
    registry = config.registry

    if not hasattr(registry, 'cms_entity_resources'):
        registry.cms_entity_resources = OrderedDict()

    def register():
        log.info('===>>> Mapping %s to resource %s', entity, resource)
        registry.cms_entity_resources[entity] = resource

    config.action(f'amnesiacms_entity_resource={entity}', register)


def cms_add_resource_path(config, resource_cls, path, target_cls):
    registry = config.registry

    if not hasattr(registry, 'cms_resource_paths'):
        registry.cms_resource_paths = OrderedDict()

    def register():
        log.info('===>>> Adding resource path "%s" from %s to %s', path,
                 resource_cls, target_cls)
        if resource_cls not in registry.cms_resource_paths:
            registry.cms_resource_paths[resource_cls] = OrderedDict()
        registry.cms_resource_paths[resource_cls][path] = target_cls

    config.action(f'amnesiacms_resource_path={resource_cls}{path}', register)


def cms_get_resource(request, entity):
    cfg = request.registry.cms_entity_resources
    return cfg[type(entity)]


def cms_add_content_prop(config, class_, key, type_, default=None):
    registry = config.registry

    if not hasattr(registry, 'cms_content_props'):
        registry.cms_content_props = OrderedDict()

    def register():
        log.debug(f'===>>> Adding custom prop {key} on {class_}')

        if class_ not in registry.cms_content_props:
            registry.cms_content_props[class_] = OrderedDict()

        registry.cms_content_props[class_][key] = {
            'type': type_,
            'default': default
        }

    config.action(f'amnesiacms_content_props={class_}{key}', register)


