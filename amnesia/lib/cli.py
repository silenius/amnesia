# -*- coding: utf-8 -*-

import logging
import shutil
import os
import os.path
import pathlib
import subprocess
import json

log = logging.getLogger(__name__)

PYRAMID_CONFIG = 'pyramid_config.json'


def webpack_build_assets(registry, asset_config, *args, **kwargs):
    settings = registry.settings
    build_dir = os.path.join(settings['static.build_dir'],
                             asset_config['name'])

    try:
        shutil.rmtree(build_dir)
    except FileNotFoundError as exc:
        log.warning(exc)

    # Copy package static sources to temporary build dir so that the source
    # code's repository and site-packages are not written to during the build
    # process.
    shutil.copytree(
        asset_config['asset_path'],
        build_dir,
        ignore=shutil.ignore_patterns(
            'node_modules', '__pycache__', 'bower_components'
        )
    )

    os.environ['AMNESIACMS_STATIC_DIR'] = settings['static.dir']

    worker_config = {
        'amnesiacmsStaticDir': settings['static.dir'],
    }

    worker_config_file = pathlib.Path(build_dir) / PYRAMID_CONFIG

    with worker_config_file.open('wt') as cfg:  # pylint: disable=no-member
        cfg.write(json.dumps(worker_config))

    # Download requirements (yarn)
    yarn_cmd = ['yarn', 'install']
    subprocess.run(yarn_cmd, env=os.environ, cwd=build_dir, check=True)

    # Execute build process (webpack)
    webpack_bin = os.path.join(build_dir, 'node_modules', '.bin', 'webpack')
    webpack_cfg = os.path.join(build_dir, settings.get('amnesia.webpack.config',
                                                       'webpack.common.js'))
    webpack_cmd = [webpack_bin, '--config', webpack_cfg, '--progress']
    log.info('===>>> Running %s', ' '.join(webpack_cmd))
    subprocess.run(webpack_cmd, env=os.environ, cwd=build_dir, check=True)
