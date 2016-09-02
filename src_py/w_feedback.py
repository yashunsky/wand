#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QThread
from PyQt4.QtCore import QTimer

from time import sleep

import json

from generation_widget import GenerationWidget
from simple_state_machine import StateMachine
from state_machine import OUTPUT_WIDGET
from input_generator import InputGenerator


KNOWLEDGE = '../migration_to_c/generation_knowledge.json'

POPUP_COUNT_DOWN = 2

FEEDBACK = {'calibration': (100, 100, 0, 0),
            "demo_0": (0, 0, 0, 30),
            "demo_1": (0, 0, 0, 100),
            "demo_2": (255, 255, 255, 65),
            "demo_3": (255, 0, 0, 65),
            "demo_4": (255, 255, 0, 65),
            "demo_5": (255, 0, 255, 65),
            "demo_6": (255, 255, 255, 65),
            "demo_7": (255, 127, 0, 65),
            "demo_8": (0, 255, 0, 65),
            'none': (10, 10, 10, 0)}


class DemoWidget(GenerationWidget):
    def __init__(self):
        super(DemoWidget, self).__init__()

        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

        self.all_strokes = self.knowledge['strokes'].keys()

        self.states = {value: key for key, value
                       in self.knowledge['states'].items()}

        self.split_states = {value: key for key, value
                             in self.knowledge['splitting']['states'].items()}

        self.state = None
        self.split_state = None

        self.popup_state = None

        self.popup_count_down = 0

        self.input_generator = InputGenerator(serial_port='/dev/tty.usbmodem1A1211',  # '/dev/tty.usbmodem1411',
                                              dual=True,
                                              gyro_remap=lambda g: [g[1], -g[0], g[2]])

        self.listener = QThread()

        self.state_machine = StateMachine(self.knowledge)

        self.listener.run = self.listener_thread

        self.listener.start()

        self.button.show()

        self.reset_timer = QTimer()
        self.reset_timer.setInterval(1000)
        self.reset_timer.timeout.connect(self.light_off)

    def process(self):
        if self.popup_state is not None:
            self.set_state(*self.popup_state)
        elif self.state is not None:
            if 'idle' in self.state:
                if self.split_state == 'in_action':
                    self.set_state('splitting', u'выполняется')
                else:
                    self.set_state(self.state)
            else:
                self.set_state(self.state)

    def set_popup(self, state, subtitle, count_down=POPUP_COUNT_DOWN):
        self.popup_state = (state, subtitle)
        self.popup_count_down = count_down

    def set_feedback(self, feedback):
        args = [0] + feedback[:3] + [1000, 0] + feedback[3]
        self.input_generator.set_feedback(*tuple(args))

    def listener_thread(self):
        for input_data in self.input_generator(True, '', True):
            state, split_state = self.state_machine(input_data,
                                                    self.all_strokes,
                                                    OUTPUT_WIDGET)
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

            if 'done' in self.state:
                self.set_popup('idle', self.state[5:])

            if (self.state in FEEDBACK):
                self.set_feedback(FEEDBACK[self.state])
                self.reset_timer.start()

            if self.popup_count_down > 0:
                self.popup_count_down -= input_data['delta']
            else:
                self.popup_state = None

        self.state = 'idle'

    def next_stroke(self):
        self.state_machine.next_stroke()

    def closeEvent(self, event):
        self.input_generator.stop()
        sleep(0.5)
        super(DemoWidget, self).closeEvent(event)

    def light_off(self):
        self.set_feedback(FEEDBACK['none'])
        self.reset_timer.stop()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    widget = DemoWidget()
    widget.show()
    app.exec_()
