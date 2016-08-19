#!/usr/bin/env python

import unittest

import json

import numpy as np

from src_py.input_generator import InputGenerator
from c_wrap import set_sm_data


INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'generation_knowledge.json'


class CheckSM(unittest.TestCase):

    def test_state_machine(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        states = {value: key for key, value in knowledge['states'].items()}

        input_generator = InputGenerator()

        accessible = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        access_c = sum([2 ** x for x in accessible])
        access_py = map(str, accessible)

        for sensor_data in input_generator(False, INPUT_LOG, False):

            result_c = set_sm_data(-1,
                                   sensor_data['delta'],
                                   sensor_data['acc'],
                                   sensor_data['gyro'],
                                   sensor_data['mag'],
                                   access_c)

            decoded_result = states[result_c]
            if decoded_result not in ('idle', 'calibration'):
                print decoded_result

if __name__ == '__main__':
    unittest.main()
