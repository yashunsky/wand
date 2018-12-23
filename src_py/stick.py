#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

import Tkinter as tk

from gui import Widget

from multiprocessing import Process, Pipe

import numpy as np

# from aperiodic import AperiodicFilter
from input_generator import InputGenerator


PORT = '/dev/tty.usbserial-A9IX9R77'

POPUP_COUNT_DOWN = 2

A_OFFSET = np.array([99.0, 123.0, -763.0])
G_OFFSET = np.array([-4698.0 + 68, -4965.0 + 63, 4972.0 - 67])
GYRO_SCALE = 2000.0 / 32768 / 180 * np.pi
G_CONST = 9.81
ACC_SCALE = G_CONST / 4096
PITCH = np.array([-1, 0, 0])
# ROLL = np.array([0, -1, 1])
ROLL = np.array([0, 0, -1])


ANGLES = {'A': 0.0, 'B': 0.25, 'C': 0.5, 'D': 0.75, 'E': 1}
PRECISION = 0.1

GYRO_FILTER_T = 0.01
GYRO_EDGE = 0.1


def start_gui(pipe_in, pipe_out):
    Widget(pipe_in, pipe_out)
    tk.mainloop()


def angle_between(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if 0.0 in (n1, n2):
        return 0.0

    return np.arccos(np.dot(v1 / n1, v2 / n2))


def decode(angle):
    for key, value in ANGLES.items():
        error = np.abs(angle - value)
        if error < PRECISION:
            return (key, error)
    return None


def start_uart(pipe_in, pipe_out, fsm=False):
    input_generator = InputGenerator(serial_port=PORT, baude_rate=256000)

    # gyro_filter = AperiodicFilter(GYRO_FILTER_T)

    old_display_state = None
    new_display_state = ('idle', '')

    old_sign = None
    new_sign = None

    popup_countdown = 0

    for input_data in input_generator(True, '', True):

        acc = (input_data['acc'] - A_OFFSET) * ACC_SCALE
        gyro = np.linalg.norm((input_data['gyro'] - G_OFFSET) * GYRO_SCALE)

        filtered_gyro = gyro  # gyro_filter.set_input(gyro, input_data['delta'])
        # print filtered_gyro

        if filtered_gyro < GYRO_EDGE:
            pitch_angle = angle_between(acc, PITCH) / np.pi
            roll_angle = angle_between(acc, ROLL) / np.pi

            # print 'stopped', pitch_angle, roll_angle

            p, r = decode(pitch_angle), decode(roll_angle)

            if None not in (p, r):
                new_sign = p[0] + r[0]
                if new_sign != old_sign:
                    old_sign = new_sign
                    popup_countdown = 1
                    new_display_state = ('splitting',
                                         '%s%s\n[%1.2f:%1.2f]' %
                                         (p[0], r[0], p[1], r[1]))

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
                old_sign = None
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
