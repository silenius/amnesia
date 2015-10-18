# -*- coding: utf-8 -*-

import csv
import io
import urllib
import os.path
import sys

import transaction

from sqlalchemy import engine_from_config
from sqlalchemy import orm, sql
from sqlalchemy.orm.exc import NoResultFound

from pyramid.scripts.common import parse_vars
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

from ..models import DBSession
from ..models import MimeMajor
from ..models import Mime
from ..models import init_models
from ..models import meta

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
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    meta.bind = engine
    meta.reflect()

    init_models()

    for t in sorted(TYPES):
        try:
            major = DBSession.query(MimeMajor).filter_by(name=t).one()
        except NoResultFound:
            major = MimeMajor(name=t)

            DBSession.add(major)

        url = '{0}{1}.csv'.format(SRC, t)
        print('===>>> Process {}'.format(url))

        with urllib.request.urlopen(url) as f:
            for row in csv.DictReader(io.StringIO(f.read().decode('utf-8'))):
                try:
                    filters = sql.and_(
                        sql.func.lower(Mime.name) == row['Name'].lower(),
                        Mime.major == major
                    )

                    minor = DBSession.query(Mime).join(Mime.major)\
                        .options(orm.contains_eager(Mime.major))\
                        .filter(filters).one()
                except NoResultFound:
                    minor = Mime(name=row['Name'], template=row['Template'],
                                 major=major)

                    DBSession.add(minor)

        transaction.commit()
