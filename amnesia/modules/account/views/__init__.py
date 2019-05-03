# -*- coding: utf-8 -*-


def includeme(config):
    config.include('.login')
    config.include('.logout')
    config.include('.register')
    config.include('.forgot_password')
    config.include('.recover_password')
    config.include('.browse')
    config.include('.roles')
    config.include('.permissions')
