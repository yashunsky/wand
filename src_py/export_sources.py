#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import sys

from os import makedirs, listdir
from os.path import exists, join

import shutil

from core_creator import get_core
import consts as c
from convert_knowledge import convert_knowledge

STROKES_SOURCE_PATH = 'raw/source'
SMS_SOURCE_PATH = 'sms'

OUTPUT = 'output'
C_SOURCES = 'src_c'

FW_PREFIX = 'C_'
PY_PREFIX = 'PY_'

PRESETS = {
    'generation': {
        'strokes': ['charge', 'throw', 'punch', 'lift',
                    'warp', 'barrier', 'cleanse', 'singular',
                    'song', 'release', 'pwr_release'],
        'state_machine': 'generation'
    }
}


def gather_knowledge(strokes):
    data = {}

    data['strokes'] = strokes['letters']
    data['segmentation'] = strokes['segmentation']
    data['strokes_order'] = strokes['order']
    data['gyro_scale'] = c.GYRO_SCALE
    data['count_down'] = c.COUNT_DOWN

    data['g_const'] = c.G_CONST
    data['acc_scale'] = c.ACC_SCALE

    data['kp_init'] = c.KP_INIT
    data['kp_work'] = c.KP_WORK
    data['ki_init'] = c.KI_INIT
    data['ki_work'] = c.KI_WORK
    data['init_edge'] = c.INIT_EDGE

    def add_state(state_name, state_dict):
        state_dict[state_name] = len(state_dict)

    s = data['states'] = {}

    add_state('calibration', s)
    add_state('idle', s)

    for name in strokes['order']:
        add_state('done_%s' % name, s)

    data['splitting'] = {}

    data['splitting']['gyro_min'] = c.GYRO_MIN
    data['splitting']['gyro_timeout'] = c.GYRO_TIMEOUT
    data['splitting']['min_length'] = c.MIN_STROKE_LENGTH
    data['splitting']['compare_limit'] = c.COMPARE_LIMIT

    s = data['splitting']['states'] = {}

    add_state('in_action', s)
    add_state('not_in_action', s)
    add_state('stroke_done', s)
    add_state('too_short', s)
    add_state('too_long', s)
    add_state('too_small', s)
    add_state('unsupported', s)
    add_state('strange', s)

    data['splitting']['min_dimention'] = c.MIN_DIMENTION
    data['splitting']['acceleration_time_const'] = c.ACCELERATION_TIME_CONST

    return data


def is_c_file(filename):
    return (filename.endswith('.h') or
            filename.endswith('.cpp') or
            filename.endswith('.c'))


def is_non_desctop_c_file(filename):
    return (is_c_file(filename) and
            'desktop' not in filename and
            filename not in ('main.c', 'bsp.h'))


def copy_c_sources(src, dst, fw=True, is_needed=lambda x: True):
    for filename in listdir(src):
        if is_needed(filename):
            if filename.startswith(FW_PREFIX):
                dst_filename = filename[len(FW_PREFIX):] if fw else None
            elif filename.startswith(PY_PREFIX):
                dst_filename = filename[len(PY_PREFIX):] if not fw else None
            else:
                dst_filename = filename
            if dst_filename is not None:
                shutil.copy(join(src, filename), join(dst, dst_filename))


def main(preset, fw=False):
    stroke_names = preset['strokes']
    strokes = get_core(stroke_names, STROKES_SOURCE_PATH, c.SEGMENTATION)
    knowledge = gather_knowledge(strokes)
    h_text, c_text = convert_knowledge(knowledge)

    if not exists(OUTPUT):
        makedirs(OUTPUT)

    with open(join(OUTPUT, 'knowledge.h'), 'w') as f:
        f.write(h_text)

    with open(join(OUTPUT, 'knowledge.cpp'), 'w') as f:
        f.write(c_text)

    sm = preset['state_machine']

    copy_c_sources(C_SOURCES, OUTPUT, fw, is_c_file)
    copy_c_sources(join(SMS_SOURCE_PATH, sm), OUTPUT,
                   fw, is_non_desctop_c_file)

if __name__ == '__main__':
    preset_name, dst = sys.argv[1:]
    main(PRESETS[preset_name], dst == 'fw')
