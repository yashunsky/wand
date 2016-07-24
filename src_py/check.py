#!/usr/bin/env python
# -*- coding: utf8 -*-

from input_generator import InputGenerator

import numpy as np

import sys

if __name__ == '__main__':
    name = sys.argv[1]
    if name == '1':
        port = '/dev/tty.usbmodem1411'
    elif name == '2':
        port = '/dev/tty.usbmodem1421'
    else:
        quit()

    gyro = np.array([0, 0, 0])

    g = InputGenerator(port)

    try:
        for data in g(True):
            gyro = np.vstack((gyro, data['gyro']))
    except KeyboardInterrupt:
        pass

    np.savetxt(name + '.log', gyro)
