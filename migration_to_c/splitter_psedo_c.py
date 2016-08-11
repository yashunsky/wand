#!/usr/bin/env python

from math import sqrt

from src_py.Aperiodic import AperiodicFilter


def add_vec(vr, v1, v2):
    vr[0] = v1[0] + v2[0]
    vr[1] = v1[1] + v2[1]
    vr[2] = v1[2] + v2[2]


def sub_vec(vr, v1, v2):
    vr[0] = v1[0] - v2[0]
    vr[1] = v1[1] - v2[1]
    vr[2] = v1[2] - v2[2]


def scale_vec(vr, v, k):
    vr[0] = v[0] * k
    vr[1] = v[1] * k
    vr[2] = v[2] * k


def norm(v):
    return sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def norm_inplace(v):
    scale_vec(v, v, 1 / norm(v))


def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]


def cross(vr, v1, v2):
    vr[0] = v1[1] * v2[2] - v1[2] * v2[1]
    vr[1] = - (v1[0] * v2[2] - v1[2] * v1[0])
    vr[2] = v1[0] * v2[1] - v1[1] * v2[0]


def adjust_range(range, position):
    for i in xrange(3):
        range[0][i] = min(range[0][i], position[i])
        range[1][i] = max(range[1][i], position[i])


def adjust_vec(vr, m, v):
    for i in xrange(3):
        vr[i] = m[i][0] * v[0] + m[i][1] * v[1] + m[i][2] * v[2]


class PipeSplitter(object):
    def __init__(self, knowledge):
        super(PipeSplitter, self).__init__()

        self.gyro_min = knowledge['gyro_min']
        self.gyro_time_out = knowledge['gyro_timeout']
        self.min_length = knowledge['min_length']

        self.timer = 0

        self.is_moving = False

        self.M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        self.data = []

        # calculating sroke global size vars
        self.reset_size()

        self.states = knowledge['states']

        self.min_dimention = knowledge['min_dimention']

        t = knowledge['acceleration_time_const']
        self.acceleration_filter = AperiodicFilter(t)

    def reset_size(self):
        self.positions_range = [[0, 0, 0], [0, 0, 0]]
        self.position = [0, 0, 0]
        self.speed = [0, 0, 0]

    def process_size(self, delay, acceleration):
        at = [0, 0, 0]
        at2 = [0, 0, 0]
        vt = [0, 0, 0]
        delta_p = [0, 0, 0]

        scale_vec(at, acceleration, delay)
        scale_vec(at2, acceleration, (delay * delay) / 2)

        add_vec(self.speed, self.speed, at)

        scale_vec(vt, self.speed, delay)

        add_vec(delta_p, vt, at2)

        add_vec(self.position, self.position, delta_p)

        adjust_range(self.positions_range, self.position)

    def set_data_inner(self, heading, gyro):

        self.gyro = gyro

        stroke = None
        dimention = 0
        too_short = None
        new_point = [0, 0, 0]

        if self.gyro > self.gyro_min:
            self.is_moving = True
            self.timer = self.gyro_time_out

            if len(self.data) == 0:
                x = [0, 0, 0]
                y = [heading[0], heading[1], 0]

                y_norm = norm(y)

                if y_norm != 0:
                    scale_vec(y, y, 1 / y_norm)
                else:
                    return

                z = [0., 0., 1.]

                cross(x, y, z)
                norm_inplace(x)

                self.M = [x, y, z]
                self.reset_size()

            adjust_vec(new_point, self.M, heading)

            self.data += [new_point]
        else:
            self.timer -= 1
            if self.timer == 0:
                self.timer = 0
                dimention = 0
                if self.positions_range is not None:
                    dim = [0, 0, 0]
                    sub_vec(dim, self.positions_range[1],
                            self.positions_range[0])

                    dimention = norm(dim)

                if len(self.data) > self.min_length:
                    stroke = self.data
                    too_short = False
                else:
                    too_short = True

            elif self.timer < 0:
                self.timer = -1
                self.is_moving = False

                self.data = []

        return {'is_moving': self.is_moving,
                'stroke': stroke,
                'dimention': dimention,
                'too_short': too_short}

    def set_data(self, delta, gyro, accel, heading):

        gyro = norm(gyro)

        accel = self.acceleration_filter.set_input(accel, delta)

        self.process_size(delta, accel)

        splitter_data = self.set_data_inner(heading, gyro)

        state = self.states['in_action']

        stroke = None

        if splitter_data['too_short'] is True:
            state = self.states['too_short']

        elif (splitter_data['dimention'] is not None and
              splitter_data['dimention'] < self.min_dimention):
            state = self.states['too_small']

        elif splitter_data['stroke'] is not None:
            state = self.states['stroke_done']
            stroke = splitter_data['stroke']

        elif splitter_data['is_moving'] is False:
            state = self.states['not_in_action']

        return {'state': state, 'stroke': stroke}
