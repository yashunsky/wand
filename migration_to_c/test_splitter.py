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


def choose_best(strokes, compare_limit):
    result = strokes[0][0]
    if (strokes[0][1] != 0 and
       strokes[1][1] / strokes[0][1] < compare_limit):
        result = None

    return result


class CheckSplitter(unittest.TestCase):

    def test_splitter(self):
        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        input_generator = InputGenerator()

        imu = IMU(knowledge['magnet_boundaries'])
        splitter_py = PipeSplitterPy(knowledge['splitting'])

        stroke_done = knowledge['splitting']['states']['stroke_done']

        for sensor_data in input_generator(False, INPUT_LOG, False):
            imu_state = imu.calc(sensor_data)
            state_py = splitter_py.set_data(sensor_data['delta'],
                                            imu_state['gyro'],
                                            imu_state['accel'],
                                            imu_state['heading'])

            result_c = set_imu_data(sensor_data['delta'],
                                    np.linalg.norm(imu_state['gyro']),
                                    imu_state['accel'].tolist(),
                                    imu_state['heading'].tolist())

            if state_py['state'] == stroke_done:
                strokes = get_letter(state_py['stroke'],
                                     knowledge['segmentation'],
                                     knowledge['strokes'])
                result_py = choose_best(strokes,
                                        knowledge['splitting']
                                        ['compare_limit'])

            if result_c != -1:
                assert state_py['state'] == stroke_done
                assert knowledge['strokes_order'][result_c] == result_py
            elif (state_py['state'] == stroke_done):
                assert result_py is None
            else:
                assert state_py['state'] != stroke_done

if __name__ == '__main__':
    unittest.main()
