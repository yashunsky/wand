#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json

OUTPUT = 'migration_to_c/test_knowledge.json'

STROKES = 'generation.json'

STROKE_NAMES = 'stroke_names.json'

MAGNET_BOUNDERIES = ((744, -499, -491), (1857, 530, 426))
ACCELERATION_TIME_CONST = 0.2  # s

GYRO_MIN = 1000
GYRO_TIMEOUT = 20
MIN_STROKE_LENGTH = 20

MIN_DIMENTION = 1.0  # conventional units

COMPARE_LIMIT = 1.5

COUNT_DOWN = 10

if __name__ == '__main__':

    data = {}

    with open(STROKES, 'r') as f:
        strokes = json.load(f)

    with open(STROKE_NAMES, 'r') as f:
        stroke_names = json.load(f)

    data['strokes'] = strokes['letters']
    data['segmentation'] = strokes['segmentation']
    data['magnet_boundaries'] = MAGNET_BOUNDERIES
    data['count_down'] = COUNT_DOWN

    data['sequences'] = {}
    data['sequences']['compare_limit'] = COMPARE_LIMIT

    names = stroke_names['names']
    sequences = stroke_names['sequences']

    data['stroke_names'] = names

    s_names = {name: index for index, name in enumerate(sequences)}

    def get_key_by_value(value):
        for k, v in names.items():
            if v == value:
                return k

    s_names_inv = {value: key for key, value in s_names.items()}

    data['sequences_names'] = [s_names_inv[index]
                               for index in sorted(s_names_inv.keys())]

    def add_state(state_name, state_dict):
        state_dict[state_name] = len(state_dict)

    recoded_sequences = {}

    for k, s in sequences.items():
        recoded_sequences[s_names[k]] = [get_key_by_value(x) for x in s]

    s = data['states'] = {}

    add_state('calibration', s)
    add_state('idle', s)

    for name in names:
        add_state('demo_%s' % name, s)

    for name in s_names_inv.keys():
        add_state('done_sequence_%s' % name, s)

    steps_count = max(map(len, recoded_sequences.values())) - 1

    for step in xrange(steps_count):
        add_state('in_progress_%s' % step, s)

    data['sequences']['dictionary'] = [recoded_sequences[index][1:]
                                       for index in sorted(recoded_sequences)]

    data['sequences']['init_stroke'] = recoded_sequences.values()[0][0]

    s = data['sequences']['states'] = {}

    add_state('unsupported', s)

    for name in s_names_inv.keys():
        add_state('done_sequence_%s' % name, s)

    for step in xrange(steps_count):
        add_state('in_progress_%s' % step, s)

    data['splitting'] = {}

    data['splitting']['gyro_min'] = GYRO_MIN
    data['splitting']['gyro_timeout'] = GYRO_TIMEOUT
    data['splitting']['min_length'] = MIN_STROKE_LENGTH

    s = data['splitting']['states'] = {}

    add_state('in_action', s)
    add_state('stroke_done', s)
    add_state('too_short', s)
    add_state('too_small', s)

    data['splitting']['min_dimention'] = MIN_DIMENTION
    data['splitting']['acceleration_time_const'] = ACCELERATION_TIME_CONST

    with open(OUTPUT, 'w') as f:
        json.dump(data, f, indent=1)
