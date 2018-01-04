# -*- coding: utf-8 -*-

# pylint: disable=E1101

from sqlalchemy import sql

from pyramid.view import view_config


def includeme(config):
    ''' Pyramid includeme func'''
    config.scan(__name__)
