# -*- coding: utf-8 -*-

from amnesia.exc import AmnesiaError

class PasteError(AmnesiaError):

    def __init__(self, container):
        super()
        self.container = container

    def __str__(self):
        return 'Paste into container {} failed'.format(self.container.id)
