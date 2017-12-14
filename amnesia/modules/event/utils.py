# -*- coding: utf-8 -*-

from amnesia.utils.text import fmt_datetime


def pretty_date(request, obj):
    """ Helper function to display event dates. The displayed format will be
        chosen between:
        - 19 to 20 Nov 2013
        - 19 Nov to 20 Dec 2013
        - 19 Nov 2013 to 4 May 2014 """

    if obj.starts.date() == obj.ends.date():
        return fmt_datetime(request, obj.starts)

    if obj.starts.year == obj.ends.year:
        if obj.starts.month == obj.ends.month:
            return '{0} to {1} {2} {3}'.format(
                obj.starts.strftime('%d'), obj.ends.strftime('%d'),
                obj.starts.strftime('%b'), obj.starts.strftime('%Y')
            )
        return '{0} {1} to {2} {3} {4}'.format(
            obj.starts.strftime('%d'), obj.starts.strftime('%b'),
            obj.ends.strftime('%d'), obj.ends.strftime('%b'),
            obj.starts.strftime('%Y')
        )
    return '{0} to {1}'.format(fmt_datetime(request, obj.starts),
                               fmt_datetime(request, obj.ends))
