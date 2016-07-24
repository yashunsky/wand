#!/usr/bin/env python
# -*- coding: utf8 -*-

import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    g1 = np.loadtxt('1.log')  # old
    g2 = np.loadtxt('2.log')  # new

    g2 *= 256

    g2[:, 0] += 4500
    g2[:, 1] += 4500
    g2[:, 2] -= 4500

    g2 /= 300

    g1[:, 2] *= -1

    plt.plot(g1)
    plt.plot(g2)
    plt.show()
