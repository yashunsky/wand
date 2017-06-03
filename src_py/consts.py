#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from math import pi

SEGMENTATION = 128

ACCELERATION_TIME_CONST = 0.2  # s

GYRO_MIN = 1
GYRO_TIMEOUT = 100
MIN_STROKE_LENGTH = 20

MAX_STROKE_LENGTH = 4096

GYRO_SCALE = 2000.0 / 32768 / 180 * pi

G_CONST = 9.81

ACC_SCALE = G_CONST / 4096

MIN_DIMENTION = 1.0  # conventional units

COMPARE_LIMIT = 1.5

COUNT_DOWN = 10

KP_INIT = 10.0
KI_INIT = 0.0

KP_WORK = 1.25
KI_WORK = 0.025

INIT_EDGE = 5.0
