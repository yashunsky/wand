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
        expected_pitch = [0 for i in xrange(31)]
        expected_pitch.extend([
-0.0000129771407, -0.0285492133501, -0.0547640005259,
-0.0792589312808, -0.1010267293485, -0.1201317682940,
-0.1376801346591, -0.1538118936673, -0.1674959918280,
-0.1799662529240, -0.1912019027219, -0.2016772549969,
-0.2116178988554, -0.2199291980645
            ])
        expected_pitch = iter(expected_pitch)

        expected_roll = [0 for i in xrange(31)]
        expected_roll.extend([
-0.0000671958995, -0.0102896959721, -0.0198513431794,
-0.0287402348280, -0.0370458244604, -0.0449268315667,
-0.0511151115435, -0.0561065533944, -0.0609793194461,
-0.0650030216116, -0.0694612927996, -0.0734142553262,
-0.0780162504125, -0.0812502508942
            ])
        expected_roll = iter(expected_roll)

        expected_yaw = [0 for i in xrange(31)]
        expected_yaw.extend([
0.0000557418889, -0.0025098377494, -0.0048848958068,
-0.0072329167865, -0.0094494686731, -0.0115499931893,
-0.0137438247065, -0.0160766028034, -0.0184064167549,
-0.0207389660695, -0.0229567446802, -0.0252784687839,
-0.0274220741921, -0.0298249441309
        ])
        expected_yaw = iter(expected_yaw)

        expected_direction_x = [0 for i in xrange(31)]
        expected_direction_x.extend([
-0.0000557410168, 0.0028035548168, 0.0059705240700,
0.0095051050806, 0.0131781286177, 0.0169201125758,
0.0207370672208, 0.0246408741289, 0.0285292559561,
0.0323182998844, 0.0360856467136, 0.0398956163053,
0.0436991560093, 0.0474203730763])
        expected_direction_x = iter(expected_direction_x)

        expected_direction_y = [1 for i in xrange(31)]
        expected_direction_y.extend([
0.9999999961888, 0.9999431700721, 0.9997857284320,
0.9995444218266, 0.9992339671884, 0.9988621596827,
0.9985032123083, 0.9981593033359, 0.9977852634508,
0.9974323396333, 0.9970229077851, 0.9966163932787,
0.9961346122551, 0.9957297449738])
        expected_direction_y = iter(expected_direction_y)

        expected_direction_z = [0 for i in xrange(31)]
        expected_direction_z.extend([
-0.0000671958994, -0.0102853180428, -0.0198202760414,
-0.0286460600840, -0.0368484987874, -0.0445880308451,
-0.0506093643475, -0.0554150870569, -0.0600886756959,
-0.0639081762408, -0.0681406408795, -0.0718617009557,
-0.0761985395798, -0.0792059526299])
        expected_direction_z = iter(expected_direction_z)

        imu = IMU.IMU(((744, -499, -491), (1857, 530, 426)))
        data_file = os.path.join(DATA_PATH, 'imu_test_data')
        with open(data_file, 'r') as f:
            data = f.readlines()
        data = map(lambda a: map(float, a.split()), data)
        for p_id, data_point in enumerate(data):
            imu.calc(data_point)

            real_pitch = imu.angles['pitch']
            real_roll = imu.angles['roll']
            real_yaw = imu.angles['yaw']

            (real_direction_x,
             real_direction_y,
             real_direction_z) = imu.get_y_direction()
            # I know that you want to delete this commented code,
            # but don't do it it is very useful when the algorytm
            # is changed more than just refactored :)
            # print '%.13f,' % real_pitch,
            # if p_id % 3 == 0:
            #     print
            assertAlmostEqual(real_pitch, next(expected_pitch))
            assertAlmostEqual(real_roll, next(expected_roll))
            assertAlmostEqual(real_yaw, next(expected_yaw))

            assertAlmostEqual(real_direction_x, next(expected_direction_x))
            assertAlmostEqual(real_direction_y, next(expected_direction_y))
            assertAlmostEqual(real_direction_z, next(expected_direction_z))


if __name__ == '__main__':
    unittest.main()
