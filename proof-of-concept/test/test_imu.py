import _preamble

import os
import unittest

import IMU

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_data')
EPSILON = 0.0000000000001


def assertAlmostEqual(real, expected):
    assert abs(real - expected) < EPSILON, '{r} is not equal to {e}'.format(
        r=real, e=expected)


class CheckImu(unittest.TestCase):
    def test_IMU(self):
        expected_pitch = [0 for i in xrange(33)]
        expected_pitch.extend([-0.0000129780176045, 0.0297418808236])
        expected_pitch = iter(expected_pitch)

        expected_roll = [0 for i in xrange(33)]
        expected_roll.extend([-0.0000916301917743, 0.0104123487793])
        expected_roll = iter(expected_roll)

        expected_yaw = [0 for i in xrange(33)]
        expected_yaw.extend([0.0000313074380366, 0.000218119048053])
        expected_yaw = iter(expected_yaw)

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

            assertAlmostEqual(real_pitch, next(expected_pitch))
            assertAlmostEqual(real_roll, next(expected_roll))
            assertAlmostEqual(real_yaw, next(expected_yaw))


if __name__ == '__main__':
    unittest.main()
