# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

log = logging.getLogger(__name__)

FRONTEND_ASSET_CONFIG_KEYS = {
    'name', 'build_script', 'asset_path'
}


def cms_register_frontend_asset(config, asset_name, asset_config):
    cfg = config.registry.setdefault('cms_frontend_assets', OrderedDict())

    def register():
        log.info('===>>> Registering frontend asset: {}'.format(asset_name))
        if asset_name not in cfg:
            to_reg_config = {}

            for key in FRONTEND_ASSET_CONFIG_KEYS:
                to_reg_config[key] = asset_config.get(key, None)

            cfg[asset_name] = to_reg_config

    config.action('amnesiacms_frontend_asset={}'.format(asset_name), register)


def cms_add_entity_resource(config, entity, resource):
    cfg = config.registry.setdefault('cms_entity_resources', OrderedDict())

    def register():
        log.info('===>>> Mapping {} to resource {}'.format(entity, resource))
        cfg[entity] = resource

    config.action('amnesiacms_entity_resource={}'.format(entity), register)
