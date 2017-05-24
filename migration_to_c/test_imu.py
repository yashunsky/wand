#!/usr/bin/python

import unittest

import json

from c_wrap import set_sensor_data, mahony

from test_madgwick import normalize, q_to_m, get_col

from almoste import almoste_equal, deep_almose_equal

INPUT_LOG = 'new_test_input.log'
KNOWLEDGE = 'generation_knowledge.json'

X_AXIS = 0


class CheckIMU(unittest.TestCase):

    def test_imu(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        with open(INPUT_LOG, 'r') as f:
            input_data = [json.loads(line.replace("'", '"'))
                          for line in f.readlines()]

        time = 0
        kp = knowledge['kp_init']
        ki = knowledge['ki_init']

        for sensor_data in input_data:
            imu_state_c = set_sensor_data(sensor_data['delta'],
                                          sensor_data['acc'],
                                          sensor_data['gyro'],
                                          sensor_data['mag'],
                                          X_AXIS)

            in_calibration, gyro, accel, heading = imu_state_c

            data = normalize(sensor_data)

            dt = data['delta']

            time += dt

            if time > knowledge['init_edge']:
                kp = knowledge['kp_work']
                ki = knowledge['ki_work']

            gx, gy, gz = data['gyro']
            ax, ay, az = data['acc']
            mx, my, mz = data['mag']

            qs = mahony(kp, ki, dt, gx, gy, gz, ax, ay, az, mx, my, mz)

            qw, qx, qy, qz = qs

            print 'py: ', qs

            v = get_col(q_to_m(qw, qx, qy, qz), 0)

            #assert deep_almose_equal(v, heading)


if __name__ == '__main__':
    unittest.main()
