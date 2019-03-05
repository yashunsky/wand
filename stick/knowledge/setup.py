#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import utils.tiny_numpy as np

PORT = '/dev/tty.usbmodem1411'

OFFSETS = {
    0: {'A': np.array([-70, -254, 101]), 'G': np.array([26, -226, 17])},
    1: {'A': np.array([85, -85, 47]), 'G': np.array([15, -123, 15])}
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

VIBRO_ON_POSITION_DONE = [(0.2, 50)]
VIBRO_ON_FAILURE = [(0.1, 30), (0.1, 0), (0.1, 30)]
VIBRO_ON_SPELL_DONE = [(None, 50)]

ATTACK_BLINK_TIMEOUT = 0.3
SHIELD_BLINK_TIMEOUT = 0.3
SHIELD_GAIN = 16

AUTO_REACTION = 0.1
AUTO_PAUSE = 1.0
