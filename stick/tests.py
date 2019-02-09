#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import unittest

import tiny_numpy as np
from position import decode_acc, decode_sequence


class StickFullTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        assert True

    def test_decode_acc(self):
        pitch_axis = np.array([0, 1, 0])
        roll_axis = np.array([0, 0, 1])
        precision = 0.05

        def decode_inner(x, y, z):
            decoded = decode_acc(np.array([x, y, z]),
                                 pitch_axis, roll_axis, precision)
            return None if decoded is None else decoded[0]

        assert decode_inner(0, -1, 0) == 'Z'

        assert decode_inner(0, -1, 1) == 'Au'
        assert decode_inner(-1, -1, 0) == 'As'
        assert decode_inner(0, -1, -1) == 'Ad'

        assert decode_inner(0, 0, 1) == 'Hu'
        assert decode_inner(1, 0, 0) == 'Hs'
        assert decode_inner(0, 0, -1) == 'Hd'

        assert decode_inner(0, 1, 1) == 'Du'
        assert decode_inner(-1, 1, 0) == 'Ds'
        assert decode_inner(0, 1, -1) == 'Dd'

        assert decode_inner(0, 1, 0) == 'N'

    def test_decode_sequence(self):
        assert decode_sequence('NAuDuHuZ') == ['N', 'Au', 'Du', 'Hu', 'Z']

if __name__ == '__main__':
    unittest.main()
