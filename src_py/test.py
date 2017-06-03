#!/usr/bin/env python

import unittest

import json

from c_wrap import mahony, set_sensor_data, set_sm_data, set_fsm_data

from almoste import deep_almose_equal

LOG = 'chargeThrowRelease.txt'

AXIS_X = 0


def get_mahony(time, sensors):

    if time < 5.0:
        kp = 10.0
        ki = 0.0
    else:
        kp = 1.25
        ki = 0.025

    dt = sensors['delta']

    gx, gy, gz = sensors['gyro']
    ax, ay, az = sensors['acc']
    mx, my, mz = sensors['mag']

    return mahony(kp, ki, dt, gx, gy, gz, ax, ay, az, mx, my, mz)


class GenerationFullTest(unittest.TestCase):

    def setUp(self):
        with open(LOG, 'r') as f:
            self.data = [json.loads(l) for l in f.readlines()]

    def test_mahony(self):
        time = 0

        for line in self.data:
            sensors = line['sensors']
            dt = sensors['delta']
            time += dt

            qs = get_mahony(time, sensors)

            assert deep_almose_equal(qs, line['qs'])

    def test_imu(self):
        for line in self.data:
            sensors = line['sensors']
            dt = sensors['delta']

            imu = set_sensor_data(dt, sensors['acc'],
                                  sensors['gyro'], sensors['mag'], AXIS_X)

            assert deep_almose_equal(imu, line['imu'])

    def test_sm(self):
        for line in self.data:
            sensors = line['sensors']
            dt = sensors['delta']
            sm = set_sm_data(dt, sensors['acc'],
                             sensors['gyro'], sensors['mag'])

            assert deep_almose_equal(sm, line['sm'])

    def test_fsm(self):
        for line in self.data:
            sensors = line['sensors']
            dt = sensors['delta']
            fsm = set_fsm_data(dt, sensors['acc'],
                               sensors['gyro'], sensors['mag'])

            assert deep_almose_equal(fsm, line['fsm'])


if __name__ == '__main__':
    unittest.main()
