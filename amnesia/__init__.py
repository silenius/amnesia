# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession
from .models import Folder
from .models import Content
from .models import meta
from .models import init_models

from .resources import Root
from .resources import ContentResource


# Pyramid will happily call __getitem__ as many times as it needs to, until it
# runs out of path segments or until a resource raises a KeyError. Each
# resource only needs to know how to fetch its immediate children, the
# traversal algorithm takes care of the rest.

# A context resource becomes the subject of a view, and often has security
# information attached to it


def main(global_config, **settings):
    """
    This function returns a Pyramid WSGI application.
    """

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    meta.bind = engine
    meta.reflect()

    init_models()

    config = Configurator(root_factory=Root, settings=settings)
    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)

#    config.add_route('home', '/')
    config.scan()

    return config.make_wsgi_app()
