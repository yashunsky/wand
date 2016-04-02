#!/usr/bin/env python

import numpy as np

from Aperiodic import AperiodicFilter
from AbstractStrokeSplitter import AbstractStrokeSplitter


class PipeSplitter(AbstractStrokeSplitter):
    def __init__(self, knowledge):
        super(PipeSplitter,
              self).__init__(knowledge['gyro_min'],
                             knowledge['gyro_timeout'],
                             knowledge['min_length'])

        self.states = knowledge['states']

        self.min_dimention = knowledge['min_dimention']

        t = knowledge['acceleration_time_const']
        self.acceleration_filter = AperiodicFilter(t)

    def set_data(self, delta, gyro, accel, heading):

        gyro = np.linalg.norm(gyro)

        accel = self.acceleration_filter.set_input(accel, delta)

        super(PipeSplitter, self).process_size(delta, accel)

        splitter_data = super(PipeSplitter, self).set_data(heading, gyro)

        state = self.states['in_action']

        stroke = None

        if splitter_data['is_moving'] is False:
            state = self.states['too_short']

        elif (splitter_data['dimention'] is not None and
              splitter_data['dimention'] < self.min_dimention):
            state = self.states['too_small']

        elif splitter_data['stroke'] is not None:
            state = self.states['stroke_done']
            stroke = splitter_data['stroke']

        return {'state': state, 'stroke': stroke}
