# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from amnesia import db

# Pyramid will happily call __getitem__ as many times as it needs to, until it
# runs out of path segments or until a resource raises a KeyError. Each
# resource only needs to know how to fetch its immediate children, the
# traversal algorithm takes care of the rest.

# A context resource becomes the subject of a view, and often has security
# information attached to it


# settings = [app:main], global_config = [DEFAULT]
def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    db.DBSession.configure(bind=engine)
    db.meta.bind = engine
    db.meta.reflect()

    db.init_models()

    #init_models()

    #config = Configurator(root_factory=Root, settings=settings)
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('img', 'amnesia:static/images')

#    config.add_route('home', '/')
#    config.scan()

    return config.make_wsgi_app()
