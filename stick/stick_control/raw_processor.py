#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy

from knowledge.setup import (G_CONST,
                             ACC_SCALE,
                             GYRO_SCALE,
                             PRECISION,
                             GYRO_EDGE,
                             ACC_EDGE,
                             DELTA_ACC_EDGE,
                             STABLE_TIMEOUT,
                             PITCH_AXIS,
                             ROLL_AXIS,
                             ACTION_TIMEOUT,
                             VIBRO_ON_POSITION_DONE,
                             VIBRO_ON_FAILURE,
                             VIBRO_ON_SPELL_DONE,
                             BLINK_TIMEOUT)
from knowledge.spells import ALL_SPELLS, ALL_PREFIXES
import utils.tiny_numpy as np

from .position import decode_acc


class EffectsBuffer(object):
    def __init__(self, default=0):
        super(EffectsBuffer, self).__init__()
        self.effects = []
        self.default = default

    def set(self, values):
        self.effects = copy(values)

    def reset(self):
        self.effects = []

    def get_state(self, delta):
        if self.effects:
            timeout, value = self.effects[0]
            if timeout is None:
                return value
            time_left = timeout - delta
            if time_left > 0:
                self.effects[0] = (time_left, value)
                return value
            else:
                self.effects.pop(0)
                return self.get_state(-time_left)
        else:
            return self.default


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
        self.sequence = ''
        self.length = 0
        self.spell_time = 0.0
        self.button_pressed = False
        self.action_timeout = ACTION_TIMEOUT
        self.failed = False

        self.vibro = EffectsBuffer()
        self.color = EffectsBuffer((0, 0, 0, 0))

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
        spell = ALL_SPELLS.get(self.sequence)

        if data['button']:
            if not self.button_pressed:
                self.failed = False
                self.action_timeout = ACTION_TIMEOUT

            self.action_timeout -= data['delta']
            if self.action_timeout < 0.0:
                self.reset()
                if not self.failed:
                    self.vibro.set(VIBRO_ON_FAILURE)
                self.failed = True

            self.button_pressed = True
            self.spell_time += data['delta']

            if spell is None and self.stable_timeout < 0 and not self.failed:
                decoded = decode_acc(acc, PITCH_AXIS, ROLL_AXIS, PRECISION)
                if decoded is not None:
                    position = decoded[0]
                    if not self.sequence.endswith(position):
                        self.vibro.set(VIBRO_ON_POSITION_DONE)
                        self.action_timeout = ACTION_TIMEOUT
                        self.length += 1
                        self.sequence += position

            spell = ALL_SPELLS.get(self.sequence)

        elif self.button_pressed:
            self.button_pressed = False
            if not spell_done and spell is not None:
                self.color.set([(BLINK_TIMEOUT, spell.color)])
            spell_done = True

        if not data['button']:
            self.failed = False

        if spell_done and spell is not None:
            print('%s %2.1f' % (spell, self.spell_time))

        if spell is not None:
            if self.button_pressed:
                self.vibro.set(VIBRO_ON_SPELL_DONE)
            else:
                self.vibro.reset()

        feedback = dict(zip(['r', 'g', 'b', 'w'],
                        self.color.get_state(data['delta'])))
        feedback['vibro'] = self.vibro.get_state(data['delta'])

        result = {'delta': data['delta'],
                  'spell_time': self.spell_time,
                  'sequence': self.sequence,
                  'doing_well': self.sequence in ALL_PREFIXES,
                  'spell': spell,
                  'done': spell_done,
                  'failed': self.failed,
                  'action_timeout': self.action_timeout,
                  'feedback': feedback}

        if spell_done:
            self.reset()

        return result

    def reset(self):
        self.spell_time = 0.0
        self.sequence = ''
        self.length = 0
        self.action_timeout = 0.0
