#!/usr/bin/env python

from os import makedirs, path
from uuid import uuid1

import numpy as np

from imu import IMU
from splitter import PipeSplitter
from sequence_processor import SequenceProcessor

from unify_definition import get_letter as get_stroke

OUTPUT_MAIN = 0
OUTPUT_WIDGET = 1
OUTPUT_TEST = 2


class StateMachine(object):
    def __init__(self, knowledge):
        super(StateMachine, self).__init__()

        self.knowledge = knowledge

        self.imu = IMU(self.knowledge['magnet_boundaries'])
        self.sp = SequenceProcessor(self.knowledge['sequences'])
        self.splitter = PipeSplitter(self.knowledge['splitting'])

        self.count_down = 0

        self.state = self.knowledge['states']['calibration']

        self.next_stroke()

    def next_stroke(self):
        self.prefix = uuid1()

    def interface_callback(self, state):
        pass

    def __call__(self, sensor_data, known, output=OUTPUT_MAIN):
        imu_state = self.imu.calc(sensor_data)

        splitter_state = {"state": None, "stroke": None}
        strokes = None
        choice = None
        next_state = self.state

        split_state = None

        if not imu_state['in_calibration']:
            if self.state == self.knowledge['states']['calibration']:
                next_state = self.state = self.knowledge['states']['idle']

            splitter_state = self.splitter.set_data(sensor_data['delta'],
                                                    imu_state['gyro'],
                                                    imu_state['accel'],
                                                    imu_state['heading'])

            if (splitter_state['state'] ==
               self.knowledge['splitting']['states']['stroke_done']):
                strokes = get_stroke(splitter_state['stroke'],
                                     self.knowledge['segmentation'],
                                     self.knowledge['strokes'])

                if output != OUTPUT_TEST:
                    folder = '../raw/simple/%s' % self.prefix
                    if not path.exists(folder):
                        makedirs(folder)
                    np.savetxt('%s/%s.txt' % (folder, uuid1()),
                               splitter_state['stroke'])

                choice = self.sp.choose_best(strokes, known)
                if choice is not None:
                    next_state = (self.knowledge['states']
                                  ['demo_%s' % choice])
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
            return {'imu': imu_state, 'splitter': splitter_state,
                    'strokes': strokes, 'choice': choice,
                    'count_down': self.count_down, 'state': next_state,
                    'split_state': split_state}

            raise ValueError('Unknown ouptup mode %d' % output)
