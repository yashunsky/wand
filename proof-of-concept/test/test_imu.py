import _preamble

import os
import unittest

import IMU

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'test_data')
EPSILON = 0.000000000001


def assertAlmostEqual(real, expected):
    assert abs(real - expected) < EPSILON, '{r} is not equal to {e}'.format(
        r=real, e=expected)


class CheckImu(unittest.TestCase):
    def test_IMU(self):
        expected_pitch = [0 for i in xrange(33)]
        expected_pitch.extend([
            -0.0000129780176045, 0.0297418808236, 0.0621470700833,
            0.0972038387316, 0.135368376248, 0.177598803493, 0.223139245459,
            0.272446975765, 0.326454907219, 0.384267422655, 0.44720305108,
            0.514680251404])
        expected_pitch = iter(expected_pitch)

        expected_roll = [0 for i in xrange(33)]
        expected_roll.extend([
            -0.0000916301917743, 0.0104123487793, 0.0223024811089,
            0.0360782109514, 0.0500803505373, 0.0648511514358, 0.0815918745181,
            0.0997528688433, 0.12112045437, 0.144832120014, 0.17316223039,
            0.204466863468])
        expected_roll = iter(expected_roll)

        expected_yaw = [0 for i in xrange(33)]
        expected_yaw.extend([
            0.0000313074380366, 0.000218119048053, 0.000794250697526,
            0.00190155237843, 0.00351166562548, 0.00574976205759,
            0.00617498817434, 0.00775526511668, 0.0112834027455,
            0.0168467064479, 0.0257698163393, 0.0381516397484])
        expected_yaw = iter(expected_yaw)

        imu = IMU.IMU('stm')
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
