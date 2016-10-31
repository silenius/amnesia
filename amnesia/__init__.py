# -*- coding: utf-8 -*-

from pyramid.config import Configurator
from .resources import Root

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

    config = Configurator(settings=settings, root_factory=Root)
    config.include('.db')
    config.include('.modules.folder.mapper')
    config.include('.modules.file.mapper')
    config.include('.modules.event.mapper')

    config.add_view(
        name='browse',
        view="amnesia.modules.folder.views.browse",
        context="amnesia.modules.folder.resources.FolderResource",
        request_method="GET",
        renderer='json'
    )

#    config.add_view(view="amnesia.modules.folder.crud.read",
#                    context='amnesia.resources.FolderResource',
#                    request_method='GET')

    return config.make_wsgi_app()
