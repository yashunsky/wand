#!/usr/bin/env python

import unittest

import json

from c_wrap import set_sm_data

LOG = 'chargeThrowRelease.txt'


def encode(arr):
    return ':'.join(map(str, arr))


class GenerationFullTest(unittest.TestCase):

    def setUp(self):
        with open(LOG, 'r') as f:
            self.data = [json.loads(l) for l in f.readlines()]

    def test_sm(self):
        states = [None]
        for line in self.data:
            sensors = line['sensors']
            dt = sensors['delta']
            sm = set_sm_data(dt, sensors['acc'],
                             sensors['gyro'], sensors['mag'])

            if states[-1] != sm[0]:
                states.append(sm[0])
        assert encode([0, 1, 2, 1, 3, 1, 11, 1]) in encode(states)

if __name__ == '__main__':
    unittest.main()
