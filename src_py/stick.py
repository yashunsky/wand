#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import Tkinter as tk

from gui import Widget

from multiprocessing import Process, Pipe

import numpy as np

from stick_input_generator import StickInputGenerator as InputGenerator


PORT = '/dev/tty.usbmodem1411'

POPUP_COUNT_DOWN = 2

A_OFFSET = np.array([255, -7, 0])
G_OFFSET = np.array([0, -67, -6])


GYRO_SCALE = 2000.0 / 32768 / 180 * np.pi
G_CONST = 9.81
ACC_SCALE = G_CONST / 4096

PITCH = np.array([0, 1, 0])
ROLL = np.array([0, 0, 1])

PRECISION = 0.05

GYRO_EDGE = 0.6
ACC_EDGE = 0.5
DELTA_ACC_EDGE = 0.5

STABLE_TIMEOUT = 0.01


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

    def decode(self, acc):
        pitch_angle = angle_between(acc, PITCH) / np.pi
        roll_angle = angle_between(acc, ROLL) / np.pi

        pitch_error = np.abs(pitch_angle - self.angle)

        if pitch_error > PRECISION:
            return

        if self.roll is None:
            return self.name, pitch_error

        for key, value in self.roll.items():
            roll_error = np.abs(roll_angle - value)
            if roll_error < PRECISION:
                return self.name + key, (pitch_error, roll_error)

        return None

PITCHES = [Pitch('N', 0.0),
           Pitch('D', 0.25, {'u': 0.25, 's': 0.5, 'd': 0.75}),
           Pitch('H', 0.5, {'u': 0.0, 's': 0.5, 'd': 1.0}),
           Pitch('A', 0.75, {'u': 0.25, 's': 0.5, 'd': 0.75}),
           Pitch('Z', 1.0)]


SPELLS = {'DuZDu': u'Щит Протего',
          'DuAuDu': u'Импедимента',
          'DuHuHs': u'Силенцио',
          'DuHuZ': u'Режущее заклятие',
          'HuZHu': u'Щит Диффендо',
          'HuDuAu': u'Инкарцеро',
          'HuAuDu': u'Риктусемпра',
          'AuZAu': u'Щит Энервейт',
          'AuDuDs': u'Ступефай',
          'AuNHu': u'Конфундус',
          'NAuDuHuZ': u'Отложенная смерть',
          'HsNZ': u'Инсендио',
          'HsZN': u'Делювиум',
          'HsAsZAuDs': u'Экспеллиармус',
          'DsAuDuAsHu': u'Табула Раса',
          'NZ': u'Авада Кедавра',
          'NHuHs': u'Круцио',
          'NAuAs': u'Империо',
          'ZAuAsAuZ': u'Экзорцио',
          'DdDsDdDuDs': u'Чара, завершающая зельеварение'}


def start_gui(pipe_in, pipe_out):
    Widget(pipe_in, pipe_out)
    tk.mainloop()


def decode(acc):
    for pitch in PITCHES:
        decoded = pitch.decode(acc)
        if decoded is not None:
            return decoded
    return None


def possible(sequence):
    str_sequence = ''.join(sequence)
    return any(known.startswith(str_sequence) for known in SPELLS)


def start_uart(pipe_in, pipe_out, fsm=False):
    input_generator = InputGenerator(serial_port=PORT, baude_rate=256000)

    old_display_state = None
    new_display_state = ('idle', '')

    popup_countdown = 0

    sequence = []
    button_pressed = False

    vibro = 0
    spell = None

    stable_timeout = STABLE_TIMEOUT

    counter = 0

    spell_time = 0

    prev_acc = np.array([0, 0, 0])

    for input_data in input_generator(True, '', True):
        acc = (input_data['acc'] - A_OFFSET) * ACC_SCALE
        gyro = np.linalg.norm((input_data['gyro'] - G_OFFSET) * GYRO_SCALE)
        button = input_data['button']

        acc_instab = abs(np.linalg.norm(acc) - G_CONST)

        delta_acc = np.linalg.norm(acc - prev_acc)
        prev_acc = acc

        if input_data['delta'] > 1000:
            input_data['delta'] = 0

        input_data['delta'] *= 0.1

        counter += 1
        if counter % 10 == 0:
            pass

        if gyro > GYRO_EDGE or acc_instab > ACC_EDGE or delta_acc > DELTA_ACC_EDGE:
            stable_timeout = STABLE_TIMEOUT
        else:
            stable_timeout -= input_data['delta']

        if button_pressed and not button:
            # cast
            spell = SPELLS.get(''.join(sequence))

            if spell is not None:
                new_display_state = ('splitting', u'%s %2.2fс' % (spell, spell_time))
                popup_countdown = POPUP_COUNT_DOWN

            button_pressed = False
            vibro = 0
            sequence = []
        elif not button_pressed and button:
            spell_time = 0
            sequence = []
            button_pressed = True
            spell = None
            vibro = 0

        spell_time += input_data['delta']

        if button_pressed:
            sign = decode(acc)
            if sign is not None and stable_timeout < 0:
                sign_name = sign[0]
                if sign_name not in sequence[-1:]:
                    sequence.append(sign_name)
                    if possible(sequence):
                        vibro = len(sequence) * 20
                    else:
                        vibro = 0
                    print sequence, possible(sequence)

            new_display_state = ({'active': True,
                                  'blink': -1,
                                  'color': 1,
                                  'vibro': vibro}, ''.join(sequence))
            popup_countdown = 1
        else:
            popup_countdown -= input_data['delta']

        if popup_countdown < 0:
            popup_countdown = 0
            new_display_state = ('idle', u'')

        if new_display_state != old_display_state:
            pipe_out.send(new_display_state)
            old_display_state = new_display_state

        if pipe_in.poll():
            message = pipe_in.recv()
            if message == 'next':
                pass
            elif message == 'exit':
                input_generator.in_loop = False


if __name__ == '__main__':
    from_gui_parent, from_gui_child = Pipe()
    to_gui_parent, to_gui_child = Pipe()

    fsm = len(sys.argv) > 1 and sys.argv[1] == '-f'

    p = Process(target=start_uart, args=(from_gui_child, to_gui_parent, fsm))
    p.start()
    start_gui(to_gui_child, from_gui_parent)
    p.join()
