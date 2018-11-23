# -*- coding: utf-8 -*-

import logging

import os
import shutil
import sys

from pyramid.scripts.common import parse_vars
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: {0} <config_uri> [var=value]\n'
          '(example: "{0} development.ini")'.format(cmd))
    sys.exit(1)


def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    with bootstrap(config_uri, options=options) as env:
        registry = env['registry']

        if not hasattr(registry, 'cms_frontend_assets'):
            print('===>>> No static packages registered')
            return

        assets = registry.cms_frontend_assets

        for (plugin_name, config) in assets.items():
            if config['build_script']:
                print('===>>> Running build script for {}'.format(plugin_name))
                config['build_script'](registry, config)
