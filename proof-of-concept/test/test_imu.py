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

        expected_direction_x = [0 for i in xrange(33)]
        expected_direction_x.extend([
            -3.13062487218e-05, 9.16801480379e-05, 0.00059120319679,
            0.00160068370942, 0.00324892953075, 0.00571179758918,
            0.0118817596096, 0.0190816863383, 0.0275458197721,
            0.0374304363701, 0.0491072112504, 0.0625351562774])
        expected_direction_x = iter(expected_direction_x)

        expected_direction_y = [1 for i in xrange(33)]
        expected_direction_y.extend([
            0.999999995312, 0.99994583118, 0.999752087277,
            0.999354088712, 0.998763793582, 0.997947218563,
            0.996765569126, 0.995206671862, 0.993047816655,
            0.990301102238, 0.986637541553, 0.982269050522])
        expected_direction_y = iter(expected_direction_y)

        expected_direction_z = [0 for i in xrange(33)]
        expected_direction_z.extend([
            -9.16301916381e-05, 0.0104075519061, 0.0222575688451,
            0.0359000844221, 0.0496014082694, 0.0637862597877,
            0.0794805832122, 0.0959139690858, 0.114442663732,
            0.133800203706, 0.155352824552, 0.176738203998])
        expected_direction_z = iter(expected_direction_z)


        imu = IMU.IMU('stm')
        data_file = os.path.join(DATA_PATH, 'imu_test_data')
        with open(data_file, 'r') as f:
            data = f.readlines()
        data = map(lambda a: map(float, a.split()), data)
        for data_point in data:
            imu.calc(data_point)

            real_pitch = imu.angles['pitch']
            real_roll = imu.angles['roll']
            real_yaw = imu.angles['yaw']

            (real_direction_x,
             real_direction_y,
             real_direction_z) = imu.get_y_direction()

            assertAlmostEqual(real_pitch, next(expected_pitch))
            assertAlmostEqual(real_roll, next(expected_roll))
            assertAlmostEqual(real_yaw, next(expected_yaw))

            assertAlmostEqual(real_direction_x, next(expected_direction_x))
            assertAlmostEqual(real_direction_y, next(expected_direction_y))
            assertAlmostEqual(real_direction_z, next(expected_direction_z))


if __name__ == '__main__':
    unittest.main()
