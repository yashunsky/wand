#!/usr/bin/env python

from os import makedirs, path
from uuid import uuid1

import numpy as np

from c_wrap import set_sensor_data
from splitter import PipeSplitter

from unify_definition import get_letter as get_stroke

OUTPUT_MAIN = 0
OUTPUT_WIDGET = 1
OUTPUT_TEST = 2

X_AXIS = 0


class StateMachine(object):
    def __init__(self, knowledge):
        super(StateMachine, self).__init__()

        self.knowledge = knowledge

        self.splitter = PipeSplitter(self.knowledge['splitting'])
        self.compare_limit = self.knowledge['splitting']['compare_limit']

        self.count_down = 0

        self.state = self.knowledge['states']['calibration']

        self.next_stroke()

    def next_stroke(self):
        self.prefix = uuid1()

    def interface_callback(self, state):
        pass

    def choose_best(self, strokes, accessible):
        print ', '.join([stroke[0] for stroke in strokes])
        result = strokes[0][0]
        if (strokes[0][1] != 0 and
           strokes[1][1] / strokes[0][1] < self.compare_limit):
            result = None

        return result if result in accessible else None

    def __call__(self, sensor_data, known, output=OUTPUT_MAIN):
        imu_state_c = set_sensor_data(sensor_data['delta'],
                                      sensor_data['acc'],
                                      sensor_data['gyro'],
                                      sensor_data['mag'],
                                      X_AXIS)

        in_calibration, gyro, accel, heading = imu_state_c

        accel = np.array(accel)
        heading = np.array(heading)

        splitter_state = {"state": None, "stroke": None}
        strokes = None
        choice = None
        next_state = self.state

        split_state = None

        if not in_calibration:
            if self.state == self.knowledge['states']['calibration']:
                next_state = self.state = self.knowledge['states']['idle']

            splitter_state = self.splitter.set_data(sensor_data['delta'],
                                                    gyro,
                                                    accel,
                                                    heading)

            if (splitter_state['state'] ==
               self.knowledge['splitting']['states']['stroke_done']):

                if output != OUTPUT_TEST:
                    folder = '../raw/simple/%s' % self.prefix
                    if not path.exists(folder):
                        makedirs(folder)
                    np.savetxt('%s/%s.txt' % (folder, uuid1()),
                               splitter_state['stroke'])

                strokes = get_stroke(splitter_state['stroke'],
                                     self.knowledge['segmentation'],
                                     self.knowledge['strokes'])

                choice = self.choose_best(strokes, known)
                if choice is not None:
                    next_state = (self.knowledge['states']
                                  ['done_%s' % choice])
                else:
                    split_state = (self.knowledge['splitting']
                                   ['states']['strange'])

                self.state = self.knowledge['states']['idle']
            else:
                split_state = splitter_state['state']

        if output == OUTPUT_MAIN:
            return next_state
        elif output == OUTPUT_WIDGET:
            return (next_state, split_state)
        elif output == OUTPUT_TEST:
            return {'imu': imu_state_c, 'splitter': splitter_state,
                    'strokes': strokes, 'choice': choice,
                    'count_down': self.count_down, 'state': next_state,
                    'split_state': split_state}

            raise ValueError('Unknown ouptup mode %d' % output)
