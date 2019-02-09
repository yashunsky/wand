#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from math import pi as math_pi, sqrt, acos


class Array(object):
    def __init__(self, value):
        super(Array, self).__init__()
        self.value = value

    def __sub__(self, other):
        return Array([a - b for a, b in zip(self.value, other.value)])

    def __add__(self, other):
        return Array([a + b for a, b in zip(self.value, other.value)])

    def __truediv__(self, scale):
        return Array([a / scale for a in self.value])

    def __mul__(self, scale):
        return Array([a * scale for a in self.value])

    def __str__(self):
        return str(self.value)


class Linalg(object):
    def __init__(self):
        super(Linalg, self).__init__()

    def norm(self, array):
        return sqrt(sum([a * a for a in array.value]))


def array(value):
    return Array(value)


def dot(a, b):
    return sum([ax * bx for ax, bx in zip(a.value, b.value)])


true_abs = abs


def abs(a):
    return true_abs(a)

pi = math_pi
arccos = acos
linalg = Linalg()
