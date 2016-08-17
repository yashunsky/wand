#!/usr/bin/env python

import unittest

import json

import numpy as np

from src_py.input_generator import InputGenerator
from src_py.imu import IMU
from src_py.splitter import PipeSplitter as PipeSplitterPy
from c_wrap import set_imu_data

from src_py.unify_definition import get_letter


INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'generation_knowledge.json'


def choose_best(strokes, accessible, compare_limit):
    result = strokes[0][0]
    if (strokes[0][1] != 0 and
       strokes[1][1] / strokes[0][1] < compare_limit):
        result = None

    return result if result in accessible else None


class CheckSplitter(unittest.TestCase):

    def test_splitter(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        input_generator = InputGenerator()

        imu = IMU(knowledge['magnet_boundaries'])
        splitter_py = PipeSplitterPy(knowledge['splitting'])

        stroke_done = knowledge['splitting']['states']['stroke_done']

        accessible = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        access_c = sum([2 ** x for x in accessible])
        access_py = map(str, accessible)

        for sensor_data in input_generator(False, INPUT_LOG, False):
            imu_state = imu.calc(sensor_data)
            state_py = splitter_py.set_data(sensor_data['delta'],
                                            imu_state['gyro'],
                                            imu_state['accel'],
                                            imu_state['heading'])

            result_c = set_imu_data(sensor_data['delta'],
                                    np.linalg.norm(imu_state['gyro']),
                                    imu_state['accel'].tolist(),
                                    imu_state['heading'].tolist(),
                                    access_c)

            if result_c != -1:
                assert state_py['state'] == stroke_done
                strokes = get_letter(state_py['stroke'],
                                     knowledge['segmentation'],
                                     knowledge['strokes'])
                result_py = choose_best(strokes, access_py,
                                        knowledge['splitting']
                                        ['compare_limit'])
                assert result_c == int(result_py)
            else:
                assert state_py['state'] != stroke_done

if __name__ == '__main__':
    unittest.main()
