import json
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

from amnesia.db import get_engine
from amnesia.db import get_session_factory
from amnesia.db import get_tm_session
from amnesia.modules.country import Country

SRC = 'https://datahub.io/core/country-list/r/data.json'


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
    config.include('amnesia.db')
    config.include('amnesia.modules.country.mapper')
    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        res = urllib.request.urlopen(SRC)
        res_body = res.read()

        j = json.loads(res_body.decode('utf-8'))

        for data in j:
            print(f"===>>> {data['Name']}")
            c = Country(iso=data['Code'].lower(), name=data['Name'])
            dbsession.add(c)

if __name__ == '__main__':
    main()
