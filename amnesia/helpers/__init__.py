# -*- coding: utf-8 -*-

from pyramid.settings import asbool

from amnesia.utils.text import shorten
from amnesia.utils.text import fmt_datetime
from amnesia.utils.gravatar import gravatar
from amnesia.modules.event.utils import pretty_date
#from .content import dump_obj
from .content import polymorphic_hierarchy
