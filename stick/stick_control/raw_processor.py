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
                             ATTACK_BLINK_TIMEOUT,
                             SHIELD_BLINK_TIMEOUT)
from knowledge.spells import ALL_SPELLS, ALL_PREFIXES
import utils.tiny_numpy as np

from .position import decode_acc

OFF = (0, 0, 0, 0)


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


def decode(acc):
    return decode_acc(acc, PITCH_AXIS, ROLL_AXIS, PRECISION)


def is_instable(gyro, acc_instab, delta_acc):
    return (gyro > GYRO_EDGE or
            acc_instab > ACC_EDGE or
            delta_acc > DELTA_ACC_EDGE)


class RawToAction(object):
    def __init__(self, a_offet, g_offset):
        super(RawToAction, self).__init__()
        self.a_offet = a_offet
        self.g_offset = g_offset
        self.stable_timeout = STABLE_TIMEOUT
        self.prev_acc = np.array([0, 0, 0])
        self.spell_time = 0.0
        self.button_pressed = False
        self.action_timeout = ACTION_TIMEOUT
        self.failed = False
        self.prev_position = None
        self.action_to_inject = []
        self.with_injection = False

    def inject(self, action):
        self.action_to_inject.append(action)

    def __call__(self, data):
        result = {'delta': data['delta'], 'value': None}

        if 'acc' in data:
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

            if data['button']:
                if not self.button_pressed:
                    self.reset()

                self.button_pressed = True
                self.spell_time += data['delta']

                if not self.failed and self.stable_timeout < 0:
                    position = decode(acc)
                    if position is not None:
                        position = position[0]
                        if self.prev_position != position:
                            self.action_timeout = ACTION_TIMEOUT
                            self.prev_position = position
                            result['value'] = position

            if not data['button'] and self.button_pressed:
                self.button_pressed = False
                result['value'] = 'release'

        self.action_timeout -= data['delta']

        if self.action_timeout < 0 and not self.failed:
            self.failed = True
            result['value'] = 'failed'

        do_reset = False

        if result['value'] is None and self.action_to_inject:
            action = self.action_to_inject.pop(0)
            if action == 'release':
                result['value'] = action
                do_reset = True
            elif action != self.prev_position:
                self.action_timeout = ACTION_TIMEOUT
                self.prev_position = action
                result['value'] = action
            self.with_injection = True

        if self.with_injection:
            self.spell_time += data['delta']

        result['spell_time'] = self.spell_time
        result['action_timeout'] = self.action_timeout

        if do_reset:
            self.reset()

        return result

    def reset(self):
        self.action_timeout = ACTION_TIMEOUT
        self.failed = False
        self.prev_position = None
        self.spell_time = 0.0
        self.with_injection = False


class RawToSequence(object):
    def __init__(self, a_offet, g_offset):
        super(RawToSequence, self).__init__()

        self.raw_to_action = RawToAction(a_offet, g_offset)

        self.vibro = EffectsBuffer()
        self.color = EffectsBuffer(OFF)

        self.reset()

    def inject(self, action):
        self.auto_release = True
        self.raw_to_action.inject(action)

    def __call__(self, data):
        action = self.raw_to_action(data)

        spell_done = False

        spell = ALL_SPELLS.get(self.sequence)

        if action['value'] == 'failed':
            if spell is None:
                self.vibro.set(VIBRO_ON_FAILURE)
            else:
                self.vibro.reset()
            self.reset()
        elif action['value'] == 'release':
            spell_done = True
            if spell is not None:
                if spell.is_attack:
                    blink = [(ATTACK_BLINK_TIMEOUT, spell.color)]
                else:
                    blink = [(SHIELD_BLINK_TIMEOUT, (0, 0, 0, 255))]
                self.color.set(blink)
            self.vibro.reset()
            if spell is not None:
                print('%s %2.1f' % (spell, action['spell_time']))
        elif action['value'] is not None:
            self.sequence += action['value']
            self.vibro.set(VIBRO_ON_POSITION_DONE)
            spell = ALL_SPELLS.get(self.sequence)

        if spell is not None and action['value'] != 'release':
            self.vibro.set(VIBRO_ON_SPELL_DONE)

        if spell is not None or action['action_timeout'] < 0:
            if self.auto_release:
                self.inject('release')

        feedback = dict(zip(['r', 'g', 'b', 'w'],
                        self.color.get_state(data['delta'])))
        feedback['vibro'] = self.vibro.get_state(data['delta'])

        result = {'delta': data['delta'],
                  'spell_time': action['spell_time'],
                  'sequence': self.sequence,
                  'doing_well': self.sequence in ALL_PREFIXES,
                  'spell': spell if spell_done else None,
                  'action_timeout': action['action_timeout'],
                  'feedback': feedback}

        if spell_done:
            self.reset()

        return result

    def reset(self):
        self.sequence = ''
        self.auto_release = False
