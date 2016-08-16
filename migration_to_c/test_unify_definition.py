#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import unittest

import src_py.unify_definition as ud
import c_wrap
import numpy as np
import json


from full_test import almoste_zero, almoste_equal


STROKE_PATH = ('test_stroke.txt')

DICT_PATH = 'generation_knowledge.json'


class CheckUnifyDefinition(unittest.TestCase):

    def test_unify_stroke(self):

        segmentation = c_wrap.get_segmentation()
        max_stroke_length = c_wrap.get_stroke_max_length()

        stroke = np.loadtxt(STROKE_PATH)

        stroke_length = stroke.shape[0]

        assert stroke_length < max_stroke_length

        np_data = ud.unify_stroke(stroke, segmentation)

        c_stroke = np.vstack((stroke, np.zeros((max_stroke_length -
                                                stroke_length, 3))))

        c_data = c_wrap.unify_stroke(np.copy(c_stroke).tolist(), stroke_length)

        c_data = np.array(c_data)

        diff = np.linalg.norm(c_data - np_data)

        assert almoste_zero(diff)

    def test_check_stroke(self):

        segmentation = c_wrap.get_segmentation()

        stroke = np.loadtxt(STROKE_PATH)

        with open(DICT_PATH, 'r') as f:
            dictionary = json.load(f)

        description = dictionary['strokes']['0']

        assert segmentation == dictionary['segmentation']

        stroke = ud.unify_stroke(stroke, segmentation).tolist()

        assert almoste_equal(c_wrap.check_stroke(stroke, description),
                             ud.check_stroke(stroke, description))


if __name__ == '__main__':
    unittest.main()
