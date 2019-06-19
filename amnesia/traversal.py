# -*- coding: utf-8 -*-

import logging

from pyramid.traversal import _join_path_tuple
from pyramid.traversal import resource_path_tuple

from pyramid.interfaces import VH_ROOT_KEY
from pyramid.interfaces import IResourceURL

from zope.interface import implementer


log = logging.getLogger(__name__)


@implementer(IResourceURL)
class AmnesiaResourceURL:
    VH_ROOT_KEY = VH_ROOT_KEY

    def __init__(self, resource, request):
        from amnesia.modules.content.model import Content
        from amnesia.modules.content.resources import Entity
        if isinstance(resource, Content):
            physical_path_tuple = ('', str(resource.id))
        elif isinstance(resource, Entity):
            physical_path_tuple = ('', str(resource.entity.id))
        else:
            physical_path_tuple = resource_path_tuple(resource)

        physical_path = _join_path_tuple(physical_path_tuple)

        if physical_path_tuple != ('',):
            physical_path_tuple = physical_path_tuple + ('',)
            physical_path = physical_path + '/'

        virtual_path = physical_path
        virtual_path_tuple = physical_path_tuple

        environ = request.environ
        vroot_path = environ.get(self.VH_ROOT_KEY)

        # if the physical path starts with the virtual root path, trim it out
        # of the virtual path
        if vroot_path is not None:
            vroot_path = vroot_path.rstrip('/')
            if vroot_path and physical_path.startswith(vroot_path):
                vroot_path_tuple = tuple(vroot_path.split('/'))
                numels = len(vroot_path_tuple)
                virtual_path_tuple = ('',) + physical_path_tuple[numels:]
                virtual_path = physical_path[len(vroot_path):]

        self.virtual_path = virtual_path  # IResourceURL attr
        self.physical_path = physical_path  # IResourceURL attr
        self.virtual_path_tuple = virtual_path_tuple  # IResourceURL attr (1.5)
        self.physical_path_tuple = (
            physical_path_tuple
        )  # IResourceURL attr (1.5)


