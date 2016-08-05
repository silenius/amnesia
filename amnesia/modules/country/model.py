# -*- coding: utf-8 -*-

from amnesia.models.root import RootModel


class Country(RootModel):

    def __init__(self, **kwargs):
        super(Country, self).__init__(**kwargs)
