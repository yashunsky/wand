#!/usr/bin/env python
# -*- coding: utf8 -*-

from input_generator import InputGenerator

import numpy as np

if __name__ == '__main__':
    g = InputGenerator()

    mag_min = np.array((-519.0, -542.0, -698.0))
    mag_max = np.array((546.0, 453.0, 408.0))

    mag_min = np.array((744, -499, -491))
    mag_max = np.array((1857, 530, 426))

    try:
        for data in g(True):
            mag = np.array(data['mag'])
            mag_n = (mag - mag_min) / (mag_max - mag_min)
            print mag_n  # np.degrees(np.arctan2(mag_n[0], mag_n[1]))
    except KeyboardInterrupt:
        pass
