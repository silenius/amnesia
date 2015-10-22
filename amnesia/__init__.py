# -*- coding: utf-8 -*-

from pyramid.decorator import reify
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession
from .models import Folder
from .models import meta
from .models import init_models


class DefaultRoot():

    def get_root(self):
        return DBSession.query(Folder).filter_by(container_id=None).one()

    def __call__(self, request=None):
        return self.get_root()

get_root = DefaultRoot()

def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    meta.bind = engine
    meta.reflect()

    init_models()

    config = Configurator(root_factory=get_root, settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

#    config.add_route('home', '/')
#    config.scan()

    return config.make_wsgi_app()
