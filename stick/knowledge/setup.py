#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import utils.tiny_numpy as np

PORT = '/dev/tty.usbmodem1411'

OFFSETS = {
    0: {'A': np.array([255, -7, 0]), 'G': np.array([0, -67, -6])},
    1: {'A': np.array([255, -7, 0]), 'G': np.array([0, -67, -6])}
}

GYRO_SCALE = 2000.0 / 32768 / 180 * np.pi
G_CONST = 9.81
ACC_SCALE = G_CONST / 4096

PITCH_AXIS = np.array([0, 1, 0])
ROLL_AXIS = np.array([0, 0, 1])

PRECISION = 0.05

GYRO_EDGE = 0.6
ACC_EDGE = 0.5
DELTA_ACC_EDGE = 0.5

STABLE_TIMEOUT = 0.01

SHIELD_TIMEOUT = 5.0

ACTION_TIMEOUT = 5.0

GUI_MAX_TIMEOUT = 20
