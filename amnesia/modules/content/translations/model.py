# -*- coding: utf-8 -*-

from sqlalchemy.ext.associationproxy import association_proxy
from amnesia.modules import Base


class ContentTranslation(Base):
    ''' Holds translations '''

    content_type = association_proxy('content', 'type')
