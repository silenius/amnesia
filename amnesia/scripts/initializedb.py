# -*- coding: utf-8 -*-

import os
import sys

import bcrypt
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy import orm, sql
from sqlalchemy.orm.exc import NoResultFound

from pyramid.scripts.common import parse_vars
from pyramid.paster import get_appsettings
from pyramid.paster import setup_logging

#from ..models import DBSession
#from ..models import Account
#from ..models import Folder
#from ..models import State
#from ..models import init_models
#from ..models import meta
#
#
#def usage(argv):
#    cmd = os.path.basename(argv[0])
#    print('usage: %s <config_uri> [var=value]\n'
#          '(example: "%s development.ini")' % (cmd, cmd))
#    sys.exit(1)
#
#
#def main(argv=sys.argv):
#
#    if len(argv) < 2:
#        usage(argv)
#
#    config_uri = argv[1]
#    options = parse_vars(argv[2:])
#    setup_logging(config_uri)
#    settings = get_appsettings(config_uri, options=options)
#    engine = engine_from_config(settings, 'sqlalchemy.')
#    DBSession.configure(bind=engine)
#    meta.bind = engine
#    meta.reflect()
#
#    init_models()
#
#    admin = Account(login='admin', password=bcrypt.hashpw('admin',
#                                                          bcrypt.gensalt()),
#                    first_name='Admin', last_name='Admin', email='change@me')
#
#    published = DBSession.query(State).filter_by(name='published').one()
#
#    root_folder = Folder(title='Home', description='Home folder',
#                         owner=admin, state=published)
#
#    DBSession.add(root_folder)
#
#    transaction.commit()

