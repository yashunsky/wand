#!/usr/bin/python

from c_wrap import mahony as tagunil

from src_py.input_generator import InputGenerator
from src_py.splitter import PipeSplitter

from math import pi

from os import makedirs, path
from uuid import uuid1

import numpy as np

from terminal_size import get_terminal_size

G = [-4698, -4965, 4972]
A = [99, 123, -763]
M = [46, 46, -6]


def normalize(data):
    def offset(v1, v2):
        return [x1 - x2 for x1, x2 in zip(v1, v2)]

    return {'delta': float(data['delta']),
            'acc': [float(x) for x in offset(data['acc'], A)],
            'gyro': [scale_gyro(x) for x in offset(data['gyro'], G)],
            'mag': [float(x) for x in offset(data['mag'], M)]}


def q_to_m(qw, qx, qy, qz):
    m = [[1 - 2 * qy ** 2 - 2 * qz ** 2,
          2 * qx * qy - 2 * qz * qw,
          2 * qx * qz + 2 * qy * qw],

         [2 * qx * qy + 2 * qz * qw,
          1 - 2 * qx ** 2 - 2 * qz ** 2,
          2 * qy * qz - 2 * qx * qw],

         [2 * qx * qz - 2 * qy * qw,
          2 * qy * qz + 2 * qx * qw,
          1 - 2 * qx ** 2 - 2 * qy ** 2]]
    return m


def get_col(m, c):
    return [r[c] for r in m]


def scale_gyro(x):
    return x * 2000.0 / 32768 / 180 * pi


def print_point(x, y):
    w, h = get_terminal_size()
    xp = int((x + 1) * w / 2)
    yp = int((-y + 1) * h / 2)

    for i in xrange(h):
        if i != yp:
            print
        else:
            print ' ' * (xp - 1), '*'

if __name__ == '__main__':

    knowledge = {
        "min_length": 20,
        "gyro_timeout": 100,
        "min_dimention": None,
        "acceleration_time_const": 0.2,
        "compare_limit": 1.5,
        "states": {
            "stroke_done": 2,
            "too_short": 3,
            "unsupported": 5,
            "not_in_action": 1,
            "strange": 6,
            "in_action": 0,
            "too_small": 4
        },
        "gyro_min": 1
    }

    splitter = PipeSplitter(knowledge)

    generator = InputGenerator(serial_port='/dev/tty.usbserial-A9IX9R77',
                               dual=False, baude_rate=256000)

    time = 0
    kp = 10.0
    ki = 0.0

    prefix = uuid1()

    for data in generator(from_uart=True):
        data = normalize(data)

        dt = data['delta']

        time += dt

        if time > 5:
            kp = 1.25
            ki = 0.025

        gx, gy, gz = data['gyro']
        ax, ay, az = data['acc']
        mx, my, mz = data['mag']

        qs = tagunil(kp, ki, dt, gx, gy, gz, ax, ay, az, mx, my, mz)

        qw, qx, qy, qz = qs

        v = get_col(q_to_m(qw, qx, qy, qz), 0)

        splitter_state = splitter.set_data(data['delta'],
                                           np.array(data['gyro']),
                                           np.array(data['acc']),
                                           np.array(v))

        if splitter_state['stroke'] is not None:
            print 'done'
            folder = '../raw/simple/%s' % prefix
            if not path.exists(folder):
                makedirs(folder)
            np.savetxt('%s/%s.txt' % (folder, uuid1()),
                       splitter_state['stroke'])
