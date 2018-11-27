# -*- coding: utf-8 -*-

import argparse
import os
import sys

from pyramid.scripts.common import parse_vars
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri",
                        help="Configuration file, e.g., development.ini")
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']
    registry = request.registry

    if not hasattr(registry, 'cms_frontend_assets'):
        print('===>>> No static packages registered')
        return

    assets = registry.cms_frontend_assets

    for (plugin_name, config) in assets.items():
        if config['build_script']:
            print('===>>> Running build script for {}'.format(plugin_name))
            config['build_script'](registry, config)
