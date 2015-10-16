# -*- coding: utf-8 -*-

import urllib
import hashlib

__all__ = ['UniqueDict']


class UniqueDict(dict):

    def __setitem__(self, key, value):
        if key not in self:
            super().__setitem__(self, key, value)
        else:
            raise KeyError('Key already exists')


GRAVATAR_URL = "http://www.gravatar.com/avatar/"

def gravatar(email, size=None):
    opts = {
        'd': 'identicon'
    }

    if size:
        opts['s'] = str(size)

    url = GRAVATAR_URL
    url += hashlib.md5(self.email.encode('utf-8').lower()).hexdigest() + '?'
    url += urllib.parse.urlencode(opts)

    return url
