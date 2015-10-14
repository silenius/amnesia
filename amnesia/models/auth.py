# -*- coding: utf-8 -*-

from amnesia.models.root import RootModel


class Human(RootModel):

    def __init__(self, **kwargs):
        super(Human, self).__init__(**kwargs)
