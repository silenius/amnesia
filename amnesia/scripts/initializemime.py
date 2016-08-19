# -*- coding: utf-8 -*-

import csv
import io
import urllib
import os.path
import sys

import transaction

from sqlalchemy import engine_from_config
from sqlalchemy import orm
from sqlalchemy import sql
from sqlalchemy.orm.exc import NoResultFound

from pyramid.config import Configurator
from pyramid.scripts.common import parse_vars
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from ..db import get_engine
from ..db import get_session_factory
from ..db import get_tm_session

from ..modules.mime import Mime
from ..modules.mime import MimeMajor

TYPES = {'application', 'audio', 'image', 'message', 'model', 'multipart',
         'text', 'video'}

SRC = 'http://www.iana.org/assignments/media-types/'


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
    settings = get_appsettings(config_uri, options=options)
    config = Configurator(settings=settings)
    config.include('..db')
    config.include('..modules.mime.mapper')
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        for t in sorted(TYPES):
            try:
                major = dbsession.query(MimeMajor).filter_by(name=t).one()
            except NoResultFound:
                major = MimeMajor(name=t)

                dbsession.add(major)

            url = '{0}{1}.csv'.format(SRC, t)
            print('===>>> Process {}'.format(url))

            with urllib.request.urlopen(url) as f:
                for row in csv.DictReader(io.StringIO(f.read().decode('utf-8'))):
                    filters = sql.and_(
                        sql.func.lower(Mime.name) == row['Name'].lower(),
                        Mime.major == major
                    )

                    try:
                        dbsession.query(Mime)\
                            .join(Mime.major)\
                            .options(orm.contains_eager(Mime.major))\
                            .filter(filters)\
                            .one()
                    except NoResultFound:
                        minor = Mime(name=row['Name'], template=row['Template'],
                                     major=major)

                        dbsession.add(minor)
