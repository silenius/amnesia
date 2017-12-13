# -*- coding: utf-8 -*-

TRUE = ('1', 'yes', 'y', True, 'true', 'on', 1)
FALSE = ('0', 'no', 'n', False, 'false', 'off', 0)

def is_true(value):
    if isinstance(value, str):
        return value.lower() in TRUE
    return value in TRUE

def is_false(value):
    if isinstance(value, str):
        return value.lower() in FALSE
    return value in FALSE

def as_list(value):
    if isinstance(value, (tuple, list, set, frozenset)):
        return value
    return [value]
