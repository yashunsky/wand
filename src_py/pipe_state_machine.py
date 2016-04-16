#!/usr/bin/env python

from pipe_imu import IMU
from pipe_splitter import PipeSplitter
from pipe_sequence_processor import SequenceProcessor

from unify_definition import get_letter as get_stroke

MODE_TRAIN = 0
MODE_DEMO = 1
MODE_RUN = 2


class GenerationStateMachine(object):
    def __init__(self, knowledge, mode, known=None):
        super(GenerationStateMachine, self).__init__()

        self.knowledge = knowledge
        self.mode = mode
        self.set_accessible_sequences(known)

        self.imu = IMU(self.knowledge['magnet_boundaries'])
        self.sp = SequenceProcessor(self.knowledge['sequences'])
        self.splitter = PipeSplitter(self.knowledge['splitting'])

        self.count_down = 0

        self.state = self.knowledge['states']['calibration']

    def set_accessible_sequences(self, known):
        self.known = known or self.knowledge['strokes'].keys()

    def interface_callback(self, state):
        pass

    def __call__(self, sensor_data):
        imu_state = self.imu.calc(sensor_data)

        next_state = self.state

        split_state = None

        if imu_state['in_calibration']:
            return (self.state, split_state)

        splitter_state = self.splitter.set_data(sensor_data['delta'],
                                                sensor_data['gyro'],
                                                imu_state['accel'],
                                                imu_state['heading'])

        if (splitter_state['state'] ==
           self.knowledge['splitting']['states']['stroke_done']):
            stroke = get_stroke(splitter_state['stroke'],
                                self.knowledge['segmentation'],
                                self.knowledge['strokes'])

            if self.mode == MODE_TRAIN:
                pass

            elif self.mode == MODE_DEMO:
                state = self.sp.choose_best(stroke, self.known)
                if state is not None:
                    next_state = self.knowledge['states']['demo_%s' % state]
                self.state = self.knowledge['states']['idle']

            elif self.mode == MODE_RUN:
                is_idle = self.state == self.knowledge['states']['idle']
                state = self.sp.next_step(stroke, self.known, is_idle)
                if (state !=
                   self.knowledge['sequences']['states']['unsupported']):
                    key = [key for key, value in
                           self.knowledge['sequences']['states'].items()
                           if value == state][0]

                    self.state = self.knowledge['states'][key]
                    next_state = self.state
                    self.count_down = self.knowledge['count_down']
                else:
                    split_state = self.knowledge['splitter']['state']['unsupported']
        else:
            split_state = splitter_state['state']

        if self.mode == MODE_RUN:
            self.count_down -= sensor_data['delta']

            if self.count_down < 0:
                self.count_down = 0
                self.state = self.knowledge['states']['idle']
                next_state = self.state

        return (next_state, split_state)
