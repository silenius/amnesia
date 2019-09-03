# -*- coding: utf-8 -*-

import argparse
import os
import os.path
import pathlib
import sys
import shutil

from pyramid.scripts.common import parse_vars
from pyramid.paster import setup_logging
from pyramid.paster import bootstrap

from hashids import Hashids

from amnesia.modules.file import File


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("config_uri",
                        help="configuration file, e.g., development.ini")
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']
    registry = request.registry
    settings = registry.settings

    hashid_salt = settings['amnesia.hashid_file_salt']
    file_storage_dir = settings['file_storage_dir']
    hashids = Hashids(salt=hashid_salt, min_length=8)

    with env['request'].tm:
        files = request.dbsession.query(File).all()

        for f in files:
            old_file = os.path.join(
                file_storage_dir,
                f.subpath,
                f.filename
            )

            if not os.path.exists(old_file):
                print("MISSING: %", old_file)

            hid = hashids.encode(f.path_name)

            new_file = pathlib.Path(
                file_storage_dir,
                'NEW',
                *(hid[:4]),
                hid + f.extension,
            )

            if not new_file.parent.exists():
                new_file.parent.mkdir(parents=True)

            try:
                print('==> ', old_file)
                shutil.copyfile(old_file, new_file)
            except (IOError, OSError) as error:
                print('Error: ', error)
