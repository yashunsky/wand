#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

import sys

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QThread

import json

from pipe_generation_widget import GenerationWidget
from pipe_state_machine import GenerationStateMachine
from pipe_state_machine import MODE_RUN, MODE_DEMO, MODE_TRAIN
from pipe_input_generator import InputGenerator


INPUT_LOG = '../migration_to_c/test_input.log'
KNOWLEDGE = '../migration_to_c/test_knowledge.json'

POPUP_COUNT_DOWN = 2

STEP_NAMES = {0: u'первый жест', 1: u'второй жест'}


class DemoWidget(GenerationWidget):
    def __init__(self, mode, from_uart=True):
        super(DemoWidget, self).__init__()

        self.from_uart = from_uart

        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

        self.states = {value: key for key, value
                       in self.knowledge['states'].items()}

        self.split_states = {value: key for key, value
                             in self.knowledge['splitting']['states'].items()}

        self.mode = mode

        self.state = None
        self.split_state = None

        self.popup_state = None

        self.popup_count_down = 0

        self.input_generator = InputGenerator()

        self.listener = QThread()

        self.state_machine = GenerationStateMachine(self.knowledge, MODE_DEMO)

        self.listener.run = self.listener_thread

        self.listener.start()

        self.next_stroke()

    def next_stroke(self):
        self.state_machine.next_stroke()

    def process(self):
        if self.popup_state is not None:
            self.set_state(*self.popup_state)
        elif self.state is not None:
            if 'in_progress' in self.state:
                step_name = STEP_NAMES[int(self.state[12:])]
                self.set_state('in_progress', step_name)
                self.popup_count_down = 0
            elif 'done_sequence' in self.state:
                seq_name = (self.knowledge['sequences_names']
                            [int(self.state[14:])])
                self.set_state('done_sequence', seq_name)
                self.popup_count_down = 0
            elif 'idle' in self.state:
                if self.split_state == 'in_action':
                    self.set_state('splitting', u'выполняется')
                else:
                    self.set_state(self.state)
            else:
                self.set_state(self.state)

    def set_popup(self, state, subtitle, count_down=POPUP_COUNT_DOWN):
        self.popup_state = (state, subtitle)
        self.popup_count_down = count_down

    def listener_thread(self):
        for input_data in self.input_generator(self.from_uart,
                                               INPUT_LOG, True):
            state, split_state = self.state_machine(input_data)
            self.state = self.states[state]

            self.split_state = (None if split_state is None
                                else self.split_states[split_state])

            if self.state != 'calibration':
                if self.split_state == 'too_small':
                    self.set_popup('splitting', u'слишком маленький', 1)
                elif self.split_state == 'too_short':
                    self.set_popup('splitting', u'слишком короткий', 1)
                elif self.split_state == 'strange':
                    self.set_popup('splitting', u'какой-то странный', 1)
                elif self.split_state == 'unsupported':
                    self.set_popup('splitting', u'какой-то не отсюда', 1)

            if 'demo' in self.state:
                stroke_name = self.knowledge['stroke_names'][self.state[5:]]
                self.set_popup('demo', stroke_name)

            if self.popup_count_down > 0:
                self.popup_count_down -= input_data['delta']
            else:
                self.popup_state = None

        self.state = 'idle'


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='strokes processing')
    parser.add_argument('mode', choices=['train', 'demo', 'run'])
    parser.add_argument('-v', '--virtual', action='store_true')

    args = parser.parse_args()

    modes = {'demo': MODE_DEMO, 'train': MODE_TRAIN, 'run': MODE_RUN}

    app = QApplication(sys.argv)
    widget = DemoWidget(modes[args.mode], not args.virtual)
    widget.show()
    app.exec_()
    widget.input_generator.stop()
