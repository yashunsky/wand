#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from collections import namedtuple
from enum import Enum


class House(Enum):
    GRYFFINDOR = '#ff0000'
    HUFFLEPUFF = '#fff300'
    RAVENCLAW = '#0006f2'
    SLYTHERIN = '#26ad06'

MageInner = namedtuple('Mage', ['name', 'sex', 'house'])


class Mage(Enum):
    GODRIC = MageInner('Годрик', 'M', House.GRYFFINDOR)
    SALAZAR = MageInner('Салазар', 'M', House.SLYTHERIN)
    ROWENA = MageInner('Ровена', 'F', House.RAVENCLAW)
    HELGA = MageInner('Хельга', 'F', House.HUFFLEPUFF)
