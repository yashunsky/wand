#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json

OUTPUT = 'migration_to_c/generation_knowledge.json'

STROKES = 'generation.json'

# MAGNET_BOUNDERIES = ((-519, -542, -698), (546, 453, 408))
MAGNET_BOUNDERIES = ((744, -499, -491), (1857, 530, 426))
ACCELERATION_TIME_CONST = 0.2  # s

GYRO_MIN = 1000
GYRO_TIMEOUT = 5
MIN_STROKE_LENGTH = 10

MIN_DIMENTION = 1.0  # conventional units

COMPARE_LIMIT = 1.5

COUNT_DOWN = 10

if __name__ == '__main__':

    data = {}

    with open(STROKES, 'r') as f:
        strokes = json.load(f)

    data['strokes'] = strokes['letters']
    data['segmentation'] = strokes['segmentation']
    data['magnet_boundaries'] = MAGNET_BOUNDERIES
    data['count_down'] = COUNT_DOWN

    def add_state(state_name, state_dict):
        state_dict[state_name] = len(state_dict)

    recoded_sequences = {}

    s = data['states'] = {}

    add_state('calibration', s)
    add_state('idle', s)

    for name in data['strokes']:
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
