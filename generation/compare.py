#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Selector import Selector

import json

CORE_STROKES_FILE = 'generation.json'
CORE_STROKES_NAMES = 'stroke_names.json'

CELL_WIDTH = 15


if __name__ == '__main__':

    selector = Selector(CORE_STROKES_FILE)

    with open(CORE_STROKES_NAMES, 'r') as f:
        strokes = json.load(f)

        strokes_names = strokes['names']
        sequences = strokes['sequences']

    def format_cell(text):
        if text in strokes_names:
            text = strokes_names[text]
        else:
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
