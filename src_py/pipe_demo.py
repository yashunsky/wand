#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QThread

import json
from time import sleep

from uuid import uuid1
from pipe_generation_widget import GenerationWidget
from pipe_state_machine import GenerationStateMachine
from pipe_state_machine import MODE_RUN, MODE_DEMO


INPUT_LOG = '../migration_to_c/test_input.log'
KNOWLEDGE = '../migration_to_c/test_knowledge.json'


def input_generator(input_log, realtime=False):
    with open(input_log, 'r') as f:
        for line in f:
            data = map(float, line.split())
            if realtime:
                sleep(data[0])
            yield {'delta': data[0],
                   'acc': data[1:4],
                   'mag': data[4:7],
                   'gyro': data[7:10]}


class DemoWidget(GenerationWidget):
    def __init__(self, mode):
        super(DemoWidget, self).__init__()

        with open(KNOWLEDGE, 'r') as f:
            knowledge = json.load(f)

        self.states = {value: key for key, value
                       in knowledge['states'].items()}

        self.mode = mode

        self.state = None
        self.prev_state = None

        self.listener = QThread()

        self.state_machine = GenerationStateMachine(knowledge, MODE_RUN)

        self.listener.run = self.listener_thread

        self.listener.start()

        self.next_stroke()

    def process(self):
        if self.prev_state != self.state:
            if 'demo' in self.state:
                self.set_state('demo', self.state)
            elif 'in_progress' in self.state:
                self.set_state('in_progress', self.state)
            elif 'done_sequence' in self.state:
                self.set_state('done_sequence', self.state)
            else:
                self.set_state(self.state)
            self.prev_state = self.state

    def listener_thread(self):
        for input_data in input_generator(INPUT_LOG, True):
            self.state = self.states[self.state_machine(input_data)]

    def next_stroke(self):
        self.prefix = uuid1()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = DemoWidget(sys.argv[1])
    widget.show()
    sys.exit(app.exec_())
