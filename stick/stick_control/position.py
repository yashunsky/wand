#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import chain

import utils.tiny_numpy as np


def angle_between(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if 0.0 in (n1, n2):
        return 0.0

    return np.arccos(np.dot(v1 / n1, v2 / n2))


class Pitch(object):
    def __init__(self, name, angle, roll=None):
        self.name = name
        self.angle = angle
        self.roll = roll

    def decode(self, acc, pitch_axis, roll_axis, precision):
        pitch_angle = angle_between(acc, pitch_axis) / np.pi
        roll_angle = angle_between(acc, roll_axis) / np.pi

        # print(pitch_angle, roll_angle)

        pitch_error = np.abs(pitch_angle - self.angle)

        if pitch_error > precision:
            return

        if self.roll is None:
            return self.name, pitch_error

        for key, value in self.roll.items():
            roll_error = np.abs(roll_angle - value)
            if roll_error < precision:
                return self.name + key, (pitch_error, roll_error)

        return None

    def positions(self):
        subkeys = [''] if self.roll is None else self.roll.keys()
        return [self.name + key for key in subkeys]

PITCHES = [Pitch('N', 0.0),
           Pitch('D', 0.25, {'u': 0.25, 's': 0.5, 'd': 0.75}),
           Pitch('H', 0.5, {'u': 0.0, 's': 0.5, 'd': 1.0}),
           Pitch('A', 0.75, {'u': 0.25, 's': 0.5, 'd': 0.75}),
           Pitch('Z', 1.0)]

POSITIONS = set(chain(*[p.positions() for p in PITCHES]))


def decode_acc(acc, pitch_axis, roll_axis, precision):
    for pitch in PITCHES:
        decoded = pitch.decode(acc, pitch_axis, roll_axis, precision)
        if decoded is not None:
            return decoded
    return None


def decode_sequence(sequence):
    extended = sequence.replace('N', 'N ').replace('Z', 'Z ')
    keys = [extended[i:i + 2].strip() for i in range(0, len(extended), 2)]

    if set(keys) - POSITIONS:
        return None

    return keys
