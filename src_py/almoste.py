#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from numpy import ndarray

EPSILON = 0.0001


def almoste_equal(a, b, absolute=False):
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if absolute:
        result = abs(a - b) < EPSILON
    else:
        result = a == b == 0 or almoste_zero(1 - (a / b) if b != 0 else (b / a))

    if not result:
        print a, b, absolute

    return result


def almoste_zero(value):
    return abs(value) < EPSILON


def deep_almose_equal(a, b, absolute=False):
    if isinstance(a, dict):
        return all((deep_almose_equal(a[key], b[key], absolute) for key in a))
    elif isinstance(a, str) or isinstance(a, unicode) or a is None:
        return a == b
    elif isinstance(a, tuple) or isinstance(a, list) or isinstance(a, ndarray):
        return all((deep_almose_equal(_a, _b, absolute) for _a, _b in zip(a, b)))
    else:
        return almoste_equal(a, b, absolute)
