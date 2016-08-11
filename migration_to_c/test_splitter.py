#!/usr/bin/env python

import unittest

import json

import numpy as np

from src_py.input_generator import InputGenerator
from src_py.imu import IMU
from src_py.splitter import PipeSplitter as PipeSplitterPy
from splitter_psedo_c import PipeSplitter as PipeSplitterC

from full_test import almoste_zero

INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'test_knowledge.json'


class CheckSplitter(unittest.TestCase):

    def test_splitter(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        input_generator = InputGenerator()

        imu = IMU(knowledge['magnet_boundaries'])
        splitter_py = PipeSplitterPy(knowledge['splitting'])
        splitter_psedo_c = PipeSplitterC(knowledge['splitting'])

        for sensor_data in input_generator(False, INPUT_LOG, False):
            imu_state = imu.calc(sensor_data)
            state_py = splitter_py.set_data(sensor_data['delta'],
                                            imu_state['gyro'],
                                            imu_state['accel'],
                                            imu_state['heading'])

            state_pcedo_c = splitter_psedo_c.set_data(sensor_data['delta'],
                                                      imu_state['gyro'],
                                                      imu_state['accel'],
                                                      imu_state['heading'])
            assert state_py['state'] == state_pcedo_c['state']

            if state_py['stroke'] is None and state_pcedo_c['stroke'] is None:
                continue

            diff = np.linalg.norm(state_py['stroke'] - state_pcedo_c['stroke'])

            assert almoste_zero(diff)

if __name__ == '__main__':
    unittest.main()
