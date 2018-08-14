# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

log = logging.getLogger(__name__)

FRONTEND_ASSET_CONFIG_KEYS = (
    'name', 'build_script', 'asset_path'
)


def cms_register_frontend_asset(config, asset_name, asset_config):
    registry = config.registry
    if not hasattr(registry, 'cms_frontend_assets'):
        registry.cms_frontend_assets = OrderedDict()

    def register():
        log.info('Registering frontend asset: {}'.format(asset_name))
        if asset_name not in config.registry.cms_frontend_assets:
            to_reg_config = {}

            for key in FRONTEND_ASSET_CONFIG_KEYS:
                to_reg_config[key] = asset_config.get(key, None)

            registry.cms_frontend_assets[asset_name] = to_reg_config

    config.action('amnesiacms_frontend_asset={}'.format(asset_name), register)
