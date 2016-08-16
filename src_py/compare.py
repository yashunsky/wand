#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import numpy as np

from unify_definition import get_letter

CORE_STROKES_FILE = '../generation.json'

CELL_WIDTH = 10


class Selector(object):
    def __init__(self, path):

        self.letters_dict = {}

        with open(path, 'r') as f:
            data = json.load(f)
            letters_lists = data['letters']
            for key, item in letters_lists.items():
                self.letters_dict[key] = np.array(item)
            self.segmentation = data['segmentation']

    def check_stroke(self, stroke):
        letters = get_letter(stroke, self.segmentation,
                             self.letters_dict)
        return letters


if __name__ == '__main__':

    selector = Selector(CORE_STROKES_FILE)

    strokes_names = selector.letters_dict

    def format_cell(text):
        if text not in strokes_names:
            try:
                text = '{: .5f}'.format(float(text))
            except ValueError:
                pass
        return (u'{: >%d}' % CELL_WIDTH).format(text)

    matrix = None

    keys = sorted(strokes_names.keys(), reverse=True)

    for key in keys:
        stroke = selector.letters_dict[key][:, :3]
        column = selector.check_stroke(stroke)
        column.sort(key=lambda x: x[0], reverse=True)
        column = [(u'', key)] + column
        column = [map(format_cell, row) for row in column]
        column = [''.join(row)
                  if matrix is None else row[-1] for row in column]

        if matrix is None:
            matrix = column
        else:
            matrix = [row1 + row2 for row1, row2 in zip(matrix, column)]
    print '\n'.join(matrix)
