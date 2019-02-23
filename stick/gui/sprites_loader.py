#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk

ROOT = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'sprites')

NAMES = ['Z', 'Au', 'As', 'Ad', 'Hu', 'Hs', 'Hd', 'Du', 'Ds', 'Dd', 'N']
SIDES = ['left', 'right']


def get_sprites():
    sprites = {}
    for side in SIDES:
        for name in NAMES:
            key = (side, name)
            filepath = os.path.join(ROOT, side, '%s.gif' % name)
            image = tk.PhotoImage(file=filepath)
            sprites[key] = {'data': image,
                            'width': image.width(),
                            'height': image.height()}
    return sprites
