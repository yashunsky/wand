#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PyQt4.QtGui import QApplication

from generation_widget import GenerationWidget
from listener import Listener
from IMU import IMU

from Aperiodic import AperiodicFilter

from AbstractStrokeSplitter import AbstractStrokeSplitter

from Selector import Selector

import numpy as np

from uuid import uuid1

from os import makedirs, path

import json

MODES = ['train', 'demo', 'init']

MAGNET_BOUNDERIES = ((744, -499, -491), (1857, 530, 426))
ACCELERATION_TIME_CONST = 0.2  # s
ACCELERATION_RESET = 10  # conventional units

GYRO_MIN = 1000
GYRO_TIMEOUT = 20
MIN_STROKE_LENGTH = 20

MIN_DIMENTION = 1.0  # conventional units

COMPARE_LIMIT = 1.5

CORE_STROKES_FILE = '../generation.json'
CORE_STROKES_NAMES = '../stroke_names.json'


class IMUwithCallback(IMU):
    def __init__(self, widget):
        super(IMUwithCallback, self).__init__(MAGNET_BOUNDERIES)
        self.widget = widget
        self.first_calibration = True

    def calc(self, data):
        if self.in_calibration:
            self.widget.set_state('calibration')
        elif self.first_calibration:
            self.widget.set_state('wait_for_%s' % self.widget.mode)
            self.first_calibration = False
        super(IMUwithCallback, self).calc(data)


class StrokeSplitter(AbstractStrokeSplitter):
    def __init__(self, parent):
        super(StrokeSplitter, self).__init__(GYRO_MIN, GYRO_TIMEOUT,
                                             MIN_STROKE_LENGTH)
        self.widget = parent

        self.selector = Selector(CORE_STROKES_FILE)

        self.current_sequence = []

        with open(CORE_STROKES_NAMES, 'r') as f:
            strokes = json.load(f)

            self.strokes_names = strokes['names']
            self.sequences = strokes['sequences']

    def on_gyro(self, is_moving):
        if is_moving:
            self.widget.set_state('%s_in_progress' % self.widget.mode)
        else:
            next_state = (self.widget.state if self.widget.mode == 'init'
                          else 'wait_for_%s' % self.widget.mode)
            self.widget.set_state(next_state, u'этот был слишком коротким')
            self.widget.reset_state(next_state, 2)

    def format_letter(self, input_tuple):
        letter, error = input_tuple
        return u'{letter}: {error:.2f}'.format(letter=letter, error=error)

    def replace_name(self, input_tuple):
        letter, error = input_tuple
        return (self.strokes_names[letter]
                if letter in self.strokes_names else letter, error)

    def on_stroke_done(self, data, dimention):
        if dimention < MIN_DIMENTION:
            next_state = (self.widget.state if self.widget.mode == 'init'
                          else 'wait_for_%s' % self.widget.mode)
            self.widget.set_state(next_state, u'этот был слишком маленьким')
            self.widget.reset_state(next_state, 2)
            return

        folder = '../%s/%s' % (self.widget.mode, self.widget.prefix)
        if not path.exists(folder):
            makedirs(folder)
        np.savetxt('%s/%s.txt' % (folder, uuid1()), data)

        if self.widget.mode == 'train':
            self.widget.set_state('train_done')
            self.widget.reset_state('wait_for_train', 2)

        elif self.widget.mode == 'demo':
            letters = self.selector.check_stroke(data)

            # letters = [self.format_letter(self.replace_name(letter))
            #            for letter in letters]

            # text = '\n'.join(letters)

            letters = [self.replace_name(letter) for letter in letters]

            text = letters[0][0]

            if (letters[0][1] != 0 and
               letters[1][1] / letters[0][1] < COMPARE_LIMIT):
                text = u'фигню какую-то'

            self.widget.set_state('demo_done', text)
            self.widget.reset_state('wait_for_demo', 5)

        elif self.widget.mode == 'init':
            letters = self.selector.check_stroke(data)
            letters = [self.replace_name(letter) for letter in letters]

            main_letter = letters[0][0]

            if (letters[0][1] != 0 and
               letters[1][1] / letters[0][1] < COMPARE_LIMIT):
                self.widget.set_state(self.widget.state,
                                      u'ни на что не похоже')
                self.widget.reset_state(self.widget.state, 2)
                return

            temp_seq = self.current_sequence + [main_letter]
            step = len(temp_seq)
            for name, seq in self.sequences.items():
                if seq[:step] == temp_seq:
                    self.current_sequence = temp_seq
                    if step == 2:
                        self.widget.set_state('definition_done', name)
                        self.widget.reset_state('wait_for_activate', 2)
                    elif step == 3:
                        self.widget.set_state('activation_done', name)
                        self.widget.reset_state('wait_for_init', 2)
                        self.current_sequence = []
                    break

            if main_letter in [s[0] for s in self.sequences.values()]:
                self.current_sequence = [main_letter]
                self.widget.set_state('init_done')
                self.widget.reset_state('wait_for_definition', 2)
            else:
                return


class StrokeListener(Listener):
    def __init__(self, parent):
        super(StrokeListener, self).__init__()

        self.widget = parent

        self.imu = IMUwithCallback(self.widget)
        self.acceleration_filter = AperiodicFilter(ACCELERATION_TIME_CONST)
        self.splitter = StrokeSplitter(self.widget)

    def callback(self, data):
        self.imu.calc(data)
        gyro = np.linalg.norm(np.array(data['gyro']))
        accel = self.imu.get_global_acceleration()

        accel = self.acceleration_filter.set_input(accel, data['delta'])

        accel_magnitude = np.linalg.norm(accel)

        if accel_magnitude > ACCELERATION_RESET:
            self.execute_spell()

        heading = self.imu.get_z_direction()

        self.splitter.set_data(heading, gyro)
        self.splitter.process_size(data['delta'], accel)

    def execute_spell(self):
        pass


class DemoWidget(GenerationWidget):
    def __init__(self, mode):
        super(DemoWidget, self).__init__()

        if mode not in MODES:
            quit('Unknown mode')

        self.mode = mode

        self.listener = StrokeListener(self)
        self.next_stroke()

    def process(self):
        self.listener.get_data()

    def next_stroke(self):
        self.prefix = uuid1()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = DemoWidget(sys.argv[1])
    widget.show()
    sys.exit(app.exec_())
