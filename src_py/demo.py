#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk

from gui import Widget

import json

from multiprocessing import Process, Pipe

from os import makedirs, path
from uuid import uuid1

import numpy as np

from c_wrap import set_sm_data
from input_generator import InputGenerator

PORT = '/dev/tty.usbserial-A9IX9R77'

KNOWLEDGE = '../knowledge.json'

POPUP_COUNT_DOWN = 2


def start_gui(pipe_in, pipe_out):
    Widget(pipe_in, pipe_out)
    tk.mainloop()


def start_uart(pipe_in, pipe_out):
    with open(KNOWLEDGE, 'r') as f:
        knowledge = json.load(f)

    states = {value: key for key, value in knowledge['states'].items()}

    split_states = {value: key for key, value
                    in knowledge['splitting']['states'].items()}

    input_generator = InputGenerator(serial_port=PORT, baude_rate=256000)

    old_display_state = ('idle', '')
    new_display_state = ('idle', '')

    popup_countdown = 0

    prefix = uuid1()

    def get_subtitle(split_state):
        if split_state == 'too_small':
            return u'слишком маленький'
        elif split_state == 'too_short':
            return u'слишком короткий'
        elif split_state == 'strange':
            return u'какой-то странный'

    for input_data in input_generator(True, '', True):

        state, split_state, stroke = set_sm_data(input_data['delta'],
                                                 input_data['acc'],
                                                 input_data['gyro'],
                                                 input_data['mag'])

        if stroke != 0:
            folder = '../raw/simple/%s' % prefix
            if not path.exists(folder):
                makedirs(folder)
            np.savetxt('%s/%s.txt' % (folder, uuid1()), stroke)

        state = states[state]

        if 'done_' in state:
            popup_countdown = 1
            new_display_state = ('splitting', state[5:])
        else:
            split_state = (None if split_state is None
                           else split_states.get(split_state))

            if state == 'calibration':
                new_display_state = ('calibration', '')
            else:
                subtitle = get_subtitle(split_state)
                if subtitle is not None:
                    popup_countdown = 1
                    new_display_state = ('splitting', subtitle)

                elif popup_countdown == 0:
                    if split_state == 'in_action':
                        new_display_state = ('splitting', u'выполняется')
                    else:
                        new_display_state = ('idle', u'')

        popup_countdown -= input_data['delta']

        if popup_countdown < 0:
            popup_countdown = 0

        if new_display_state != old_display_state:
            pipe_out.send(new_display_state)
            old_display_state = new_display_state

        if pipe_in.poll():
            message = pipe_in.recv()
            if message == 'next':
                prefix = uuid1()
            elif message == 'exit':
                input_generator.in_loop = False

if __name__ == '__main__':
    from_gui_parent, from_gui_child = Pipe()
    to_gui_parent, to_gui_child = Pipe()

    p = Process(target=start_uart, args=(from_gui_child, to_gui_parent))
    p.start()
    start_gui(to_gui_child, from_gui_parent)
    p.join()
