# -*- coding: utf-8 -*-

import cherrypy

from amnesia.models.root import RootModel


class State(RootModel):

    def __init__(self, **kwargs):
        super(State, self).__init__(**kwargs)

    def icon(self, size='16x16'):
        return cherrypy.url('/images/states/%s/%s.png' % (size, str(self.name)))
