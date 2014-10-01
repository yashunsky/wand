import _preamble

import os
import unittest

import IMU

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_data')
EPSILON = 0.0000000000001


class CheckImu(unittest.TestCase):
    def test_IMU(self):
        imu = IMU.IMU()
        data_file = os.path.join(DATA_PATH, 'imu_test_data')
        with open(data_file, 'r') as f:
            data = f.readlines()
        data = map(lambda a: map(float, a.split()), data)
        for data_point in data:
            imu.calc(data_point)

        real_pitch = imu.pitch
        real_roll = imu.roll
        real_yaw = imu.yaw

        expected_pitch = 0.0297418808236
        expected_roll = 0.0104123487793
        expected_yaw = 0.000218119048053

        self.assertTrue(abs(real_pitch - expected_pitch) < EPSILON)
        self.assertTrue(abs(real_roll - expected_roll) < EPSILON)
        self.assertTrue(abs(real_yaw - expected_yaw) < EPSILON)


if __name__ == '__main__':
    unittest.main()
