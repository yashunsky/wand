#!/usr/bin/env python

import unittest

import json

import numpy as np

from src_py.input_generator import InputGenerator
from src_py.imu import IMU
from c_wrap import set_sensor_data
from full_test import almoste_equal, deep_almose_equal

INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'generation_knowledge.json'

Z_AXIS = 2


class CheckIMU(unittest.TestCase):

    def test_imu(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        input_generator = InputGenerator()

        imu_py = IMU(knowledge['magnet_boundaries'])

        for sensor_data in input_generator(False, INPUT_LOG, False):
            imu_state_py = imu_py.calc(sensor_data)

            imu_state_c = set_sensor_data(sensor_data['delta'],
                                          sensor_data['acc'],
                                          sensor_data['gyro'],
                                          sensor_data['mag'],
                                          Z_AXIS)

            in_calibration, gyro, accel, heading = imu_state_c

            assert in_calibration == imu_state_py['in_calibration']
            assert almoste_equal(gyro, np.linalg.norm(imu_state_py['gyro']))
            assert deep_almose_equal(accel, imu_state_py['accel'])
            assert deep_almose_equal(heading, imu_state_py['heading'])


if __name__ == '__main__':
    unittest.main()
