#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json

from math import pi

OUTPUT = 'migration_to_c/generation_knowledge.json'

STROKES = 'generation.json'

# MAGNET_BOUNDERIES = ((-519, -542, -698), (546, 453, 408))
MAGNET_BOUNDERIES = ((744, -499, -491), (1857, 530, 426))
ACCELERATION_TIME_CONST = 0.2  # s

GYRO_MIN = 1000
GYRO_TIMEOUT = 20
MIN_STROKE_LENGTH = 20

GYRO_SCALE = 2000.0 / 32768 / 180 * pi

G_CONST = 9.81

ACC_SCALE = G_CONST / 4096

MIN_DIMENTION = 1.0  # conventional units

COMPARE_LIMIT = 1.5

COUNT_DOWN = 10

KP_INIT = 10
KI_INIT = 0

KP_WORK = 1.25
KI_WORK = 0.025

INIT_EDGE = 5

if __name__ == '__main__':

    data = {}

    with open(STROKES, 'r') as f:
        strokes = json.load(f)

    data['strokes'] = strokes['letters']
    data['segmentation'] = strokes['segmentation']
    data['strokes_order'] = strokes['order']
    data['gyro_scale'] = GYRO_SCALE
    data['count_down'] = COUNT_DOWN

    data['g_const'] = G_CONST
    data['acc_scale'] = ACC_SCALE

    data['kp_init'] = KP_INIT
    data['kp_work'] = KP_WORK
    data['ki_init'] = KI_INIT
    data['ki_work'] = KI_WORK
    data['init_edge'] = INIT_EDGE

    def add_state(state_name, state_dict):
        state_dict[state_name] = len(state_dict)

    recoded_sequences = {}

    s = data['states'] = {}

    add_state('calibration', s)
    add_state('idle', s)

    for name in strokes['order']:
        add_state('done_%s' % name, s)

    data['splitting'] = {}

    data['splitting']['gyro_min'] = GYRO_MIN
    data['splitting']['gyro_timeout'] = GYRO_TIMEOUT
    data['splitting']['min_length'] = MIN_STROKE_LENGTH
    data['splitting']['compare_limit'] = COMPARE_LIMIT

    s = data['splitting']['states'] = {}

    add_state('in_action', s)
    add_state('not_in_action', s)
    add_state('stroke_done', s)
    add_state('too_short', s)
    add_state('too_small', s)
    add_state('unsupported', s)
    add_state('strange', s)

    data['splitting']['min_dimention'] = MIN_DIMENTION
    data['splitting']['acceleration_time_const'] = ACCELERATION_TIME_CONST

    with open(OUTPUT, 'w') as f:
        json.dump(data, f, indent=1)
