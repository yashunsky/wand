#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
from os.path import join, basename
from os import walk

import numpy as np
from unify_definition import unify_stroke

SEGMENTATION = 128
SOURCE_PATH = '../raw/source'


def make_core(letters, points):
    core = {}
    for key, letters_group in letters.items():
        unified = np.array([unify_stroke(letter, points)
                            for letter in letters_group])
        centers = np.mean(unified, axis=0)

        n = np.linalg.norm(centers, axis=1)

        norms = np.vstack((n, n, n)).T

        centers = centers / norms

        core[key] = centers
    return core


def get_letters(path, strokes_set=None):
    '''Read stroke files from given folder
    and arange them into a dict of lists by key-letter'''

    letters = {}

    for (dirpath, dirnames, filenames) in walk(path):
        if dirpath == path:
            continue
        for f in sorted(filenames):
            try:
                data = np.loadtxt(join(dirpath, f))
            except ValueError:
                continue
            filename = basename(f)
            key = dirpath.split('/')[-1].split('-')[0]
            if strokes_set and key not in strokes_set:
                continue
            if key not in letters:
                letters[key] = []
            letters[key].append({'filename': filename, 'data': data})
    return strokes_set or sorted(letters.keys()), letters


def make_dict(strokes):
    return {key: [element['data'] for element in elements_list]
            for key, elements_list in strokes.items()}


def get_core(strokes, source_path=SOURCE_PATH, segmentation=SEGMENTATION):
    _, letters = get_letters(source_path, {s for s in strokes})
    core = make_core(make_dict(letters), segmentation)
    dump_data = {
        'segmentation': segmentation,
        'order': strokes,
        'letters': {key: val.tolist()
                    for key, val in core.items() if key != '_'}
    }

    return dump_data

if __name__ == '__main__':
    strokes = ['charge', 'throw', 'punch', 'lift',
               'warp', 'barrier', 'cleanse', 'singular',
               'song', 'release', 'pwr_release']
    core_path = '../generation.json'

    core = get_core(strokes)

    with open(core_path, 'w') as f:
        json.dump(core, f, indent=1)
