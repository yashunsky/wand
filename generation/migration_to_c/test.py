#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import unittest

import unify_definition_psedo_c as ud_pc
import unify_definition_np as ud_np
import numpy as np
import json

EPSILON = 0.0000000001


STROKE_PATH = ('../train/1ae92ed9-e850-11e5-8105-ac87a30aa589/' +
               '1ed90bfa-e850-11e5-a5ec-ac87a30aa589.txt')

DICT_PATH = 'migration_to_c.json'


class CheckUnifyDefinition(unittest.TestCase):

    def test_unify_stroke(self):

        segmentation = ud_pc.get_segmentation()
        max_stroke_length = ud_pc.get_stroke_max_length()

        stroke = np.loadtxt(STROKE_PATH)

        stroke_length = stroke.shape[0]

        assert stroke_length < max_stroke_length

        np_data = ud_np.unify_stroke(stroke, segmentation)

        c_stroke = np.vstack((stroke, np.zeros((max_stroke_length -
                                                stroke_length, 3))))

        pc_data = ud_pc.unify_stroke(np.copy(c_stroke), stroke_length)

        pc_data = np.array(pc_data)

        diff = np.linalg.norm(pc_data - np_data)

        assert diff < EPSILON

    def test_check_stroke(self):

        segmentation = ud_pc.get_segmentation()

        stroke = np.loadtxt(STROKE_PATH)

        with open(DICT_PATH, 'r') as f:
            dictionary = json.load(f)

        description = dictionary['letters']['e5de21f0']

        assert segmentation == dictionary['segmentation']

        stroke = ud_np.unify_stroke(stroke, segmentation).tolist()

        assert (ud_np.check_stroke(stroke, description) ==
                ud_pc.check_stroke(stroke, description))


if __name__ == '__main__':
    unittest.main()
