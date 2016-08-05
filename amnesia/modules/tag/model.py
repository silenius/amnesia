# -*- coding: utf-8 -*-

from amnesia.models.root import RootModel


class Tag(RootModel):

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)
