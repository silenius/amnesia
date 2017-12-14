# -*- coding: utf-8 -*-

# pylint: disable=E1101

from pyramid.view import view_config

from amnesia.modules.folder import Folder
from amnesia.modules.file import File


def includeme(config):
    config.scan(__name__)


@view_config(name='', request_method='GET',
             renderer='amnesia:templates/index.pt')
def index(request):
    context = {}

    _queryf = request.dbsession.query(Folder).enable_eagerloads(False)

    # Banners

    try:
        banners_home = _queryf.get(request.registry.settings['banners_container_id'])
    except KeyError:
        banners_home = None

    if banners_home:
        banners_home = request.dbsession.query(File).filter(
            File.filter_published(),
            File.filter_container_id(banners_home.id)
        ).order_by(File.weight.desc()).all()
    else:
        banners_home = ()

    context['banners'] = banners_home

    # Logos

    try:
        _subc2 = _queryf.get(request.registry.settings['logos_container_id'])
    except KeyError:
        _subc2 = None

    if _subc2:
        _sub2 = request.dbsession.query(File).filter(
            File.filter_published(),
            File.filter_container_id(_subc2.id)
        ).order_by(File.weight.desc()).all()
    else:
        _sub2 = ()

    context['logos_folder'] = _subc2
    context['logos'] = _sub2

    # Various widgets

    context['why_choose'] = request.registry.settings['why_choose_container_id']
    context['high_prio'] = request.registry.settings['high_prio_container_id']
    context['current_projects'] = request.registry.settings['our_current_projects_container_id']

    return context
