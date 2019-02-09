#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy

from setup import (G_CONST,
                   ACC_SCALE,
                   GYRO_SCALE,
                   PRECISION,
                   GYRO_EDGE,
                   ACC_EDGE,
                   DELTA_ACC_EDGE,
                   STABLE_TIMEOUT,
                   PITCH_AXIS,
                   ROLL_AXIS)

import tiny_numpy as np
from position import decode_acc


def is_instable(gyro, acc_instab, delta_acc):
    return (gyro > GYRO_EDGE or
            acc_instab > ACC_EDGE or
            delta_acc > DELTA_ACC_EDGE)


class RawToSequence(object):
    def __init__(self, a_offet, g_offset):
        super(RawToSequence, self).__init__()
        self.a_offet = a_offet
        self.g_offset = g_offset
        self.stable_timeout = STABLE_TIMEOUT
        self.prev_acc = np.array([0, 0, 0])
        self.sequence = []
        self.spell_time = 0.0
        self.button_pressed = False

    def __call__(self, data):
        acc = (np.array(data['acc']) - self.a_offet) * ACC_SCALE
        gyro = np.linalg.norm((np.array(data['gyro']) -
                               self.g_offset) * GYRO_SCALE)

        acc_instab = abs(np.linalg.norm(acc) - G_CONST)

        delta_acc = np.linalg.norm(acc - self.prev_acc)
        self.prev_acc = acc

        if is_instable(gyro, acc_instab, delta_acc):
            self.stable_timeout = STABLE_TIMEOUT
        else:
            self.stable_timeout -= data['delta']
            if self.stable_timeout < 0:
                self.stable_timeout = -1

        spell_done = False

        if data['button']:
            self.button_pressed = True
            self.spell_time += data['delta']

            if self.stable_timeout < 0:
                decoded = decode_acc(acc, PITCH_AXIS, ROLL_AXIS, PRECISION)
                if decoded is not None:
                    position = decoded[0]
                    if not self.sequence or self.sequence[-1] != position:
                        self.sequence.append(position)

        elif self.button_pressed:
            self.button_pressed = False
            spell_done = True

        result = {'delta': data['delta'],
                  'spell_time': self.spell_time,
                  'sequence': copy(self.sequence),
                  'done': spell_done}

        if spell_done:
            self.spell_time = 0.0
            self.sequence = []

        return result
