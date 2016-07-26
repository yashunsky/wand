#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import unittest

from src_py.imu import IMU
import c_wrap_imu

MAGNET_BOUNDERIES = ((744, -499, -491), (1857, 530, 426))

INPUT_LOG = 'test_input.dat'

EPSILON = 0.00001


def assert_almoste_equal_list(a, b):
    assert len(a) == len(b)
    for ax, bx in zip(a, b):
        assert almoste_equal(ax, bx)


def almoste_equal(a, b):
    return a == b == 0 or almoste_zero(1 - a / b)


def almoste_zero(value):
    return abs(value) < EPSILON


def input_generator():
    with open(INPUT_LOG, 'r') as f:
        for line in f:
            data = map(float, line.split())
            yield {'delta': data[0],
                   'acc': data[1:4],
                   'mag': data[4:7],
                   'gyro': data[7:10]}


def wrap_calc(input_data):
    inline = ([input_data['delta']] +
              input_data['acc'] + input_data['mag'] + input_data['gyro'])
    in_calibration, accel, heading = c_wrap_imu.calc(inline)
    return {'in_calibration': in_calibration,
            'accel': accel,
            'heading': heading}


class CheckIMU(unittest.TestCase):

    def test_input(self):

        imu_py = IMU(MAGNET_BOUNDERIES)

        for input_data in input_generator():
            data_c = wrap_calc(input_data)
            data_py = imu_py.calc(input_data)
            assert data_c['in_calibration'] == data_py['in_calibration']
            assert_almoste_equal_list(data_c['accel'], data_py['accel'])
            assert_almoste_equal_list(data_c['heading'], data_py['heading'])

if __name__ == '__main__':
    unittest.main()
