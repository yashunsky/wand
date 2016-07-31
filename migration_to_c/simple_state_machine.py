#!/usr/bin/env python

import numpy as np

from src_py.imu import IMU
from src_py.splitter import PipeSplitter

import c_wrap


def choose_best(stroke, accessible, knowledge):
    max_stroke_length = c_wrap.get_stroke_max_length()
    stroke_length = len(stroke)

    c_stroke = np.vstack((stroke, np.zeros((max_stroke_length -
                                            stroke_length, 3))))

    access = 0

    stroke_id = c_wrap.get_stroke(np.copy(c_stroke).tolist(),
                                  stroke_length, access)

    if stroke_id < 0:
        return None
    else:
        return knowledge['strokes_order'][stroke_id]


class StateMachine(object):
    def __init__(self, knowledge):
        super(StateMachine, self).__init__()

        self.knowledge = knowledge

        self.imu = IMU(self.knowledge['magnet_boundaries'])
        self.splitter = PipeSplitter(self.knowledge['splitting'])

        self.state = self.knowledge['states']['calibration']

    def __call__(self, sensor_data, known):
        imu_state = self.imu.calc(sensor_data)

        if imu_state['in_calibration']:
            return self.knowledge['states']['calibration']

        splitter_state = {"state": None, "stroke": None}
        choice = None
        next_state = self.state

        if self.state == self.knowledge['states']['calibration']:
            next_state = self.state = self.knowledge['states']['idle']

        splitter_state = self.splitter.set_data(sensor_data['delta'],
                                                imu_state['gyro'],
                                                imu_state['accel'],
                                                imu_state['heading'])

        if (splitter_state['state'] ==
           self.knowledge['splitting']['states']['stroke_done']):

            choice = choose_best(splitter_state['stroke'],
                                 known, self.knowledge)
            if choice is not None:
                next_state = (self.knowledge['states']
                              ['demo_%s' % choice])

            self.state = self.knowledge['states']['idle']

        return next_state

# set 0 255,255,255,100
