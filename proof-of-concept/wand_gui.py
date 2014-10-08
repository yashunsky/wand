#!/usr/bin/env python
#-*- coding: utf-8 -*-

from copy import deepcopy
import os
import serial
# uncomment to use virtual serial port
#import test.PsedoSerial as serial
import sys
from time import time

import numpy as np
from PySide.QtGui import QApplication, QWidget, QLabel
from PySide.QtGui import QGridLayout, QComboBox, QFont
from PySide.QtCore import QTimer

from IMU import IMU
from Selector import Selector
from Stroke import Stroke
from stroke_widget import StrokeWidget
from Aperiodic import AperiodicFilter


PLATFORM_SPECIFIC_QUOTIENTS = {
    'stm': ((744, -499, -491), (1857, 530, 426)),
    'arduino': ((-504, -615, -564), (597, 488, 384))
}

SERIAL_PORT = '/dev/ttyUSB0'
BAUDE_RATE = 115200
CORE_FILENAME = 'tetra_v2.txt'
LEARNED_FOLDER = 'learned'
MAX_DATA_TIMELAPSE = 0.05 #s
BUFFER_DELIMITER = '\r\n'
DISPLAY_TIMEOUT = 1000 #ms
ACCELERATION_TIME_CONST = 0.5 #s

SERIAL_INTERVAL = 20 #ms
PROCESS_INTERVAL = 100 #ms

ACCELERATION_RESET = 6000 #conventional units


class Listener(QWidget):
    def __init__(self, core_file_name):
        super(Listener, self).__init__()
        self.core_file_name = core_file_name

        self.setup_ui()
        self.setup_timers()

        port = SERIAL_PORT
        self.serial = serial.Serial(port, BAUDE_RATE, timeout=0)
        self.incoming_data = []

        self.imu = IMU(PLATFORM_SPECIFIC_QUOTIENTS['stm'])
        self.stroke = Stroke()
        self.selector = Selector(self.core_file_name)

        self.acceleration_filter = AperiodicFilter(ACCELERATION_TIME_CONST)

        self.stroke.widget = self.display
        self.stroke.on_done = self.get_stroke

        self.previous_time = None

        self.data_buffer = ''

        self.init_selector()

    def setup_ui(self):
        self.resize(500, 500)
        self.out = QLabel(self)
        self.out.setMinimumHeight(100)
        font = QFont()
        font.setPixelSize(80)
        self.out.setFont(font)
        self.grid = QGridLayout(self)
        self.display = StrokeWidget()
        self.letter_selector = QComboBox()
        self.grid.addWidget(self.display, 0, 0, 1, 1)
        self.grid.addWidget(self.letter_selector, 1, 0, 1, 1)
        self.grid.addWidget(self.out, 2, 0, 1, 1)

    def setup_timers(self):
        self.serial_timer = QTimer()
        self.serial_timer.setInterval(SERIAL_INTERVAL)
        self.serial_timer.timeout.connect(self.get_data)
        self.serial_timer.start()

        self.process_timer = QTimer()
        self.process_timer.setInterval(PROCESS_INTERVAL)
        self.process_timer.timeout.connect(self.process)
        self.process_timer.start()

        self.display_timer = QTimer()
        self.display_timer.setInterval(DISPLAY_TIMEOUT)
        self.display_timer.setSingleShot(True)
        self.display_timer.timeout.connect(self.set_background)


    def init_selector(self):
        sel_lines = self.selector.letters_dict.keys()
        sel_lines.insert(0, 'free run')
        self.letter_selector.addItems(sel_lines)
        self.letter_selector.currentIndexChanged.connect(self.set_background)

    def set_background(self):
        letter = self.letter_selector.currentText()
        self.display.set_background(self.core_file_name, letter)

    def store_stroke(self, key, stroke):
        self.display.set_background(self.core_file_name, key, color='g')
        file_name = '{key}{time}.txt'.format(key=key, time=int(time()))
        file_path = os.path.join(LEARNED_FOLDER, file_name)
        np.savetxt(file_path, stroke)
        self.display_timer.start()

    def get_stroke(self, stroke):
        try:
            letters = self.selector.check_stroke(stroke)
        except: #TODO: check unify_stroke
            return
        letter = self.letter_selector.currentText()

        if letters:
            self.out.setText(self.out.text()+letters[0])

        if letter == 'free run' and letters:
            self.store_stroke(letters[0], stroke)
        elif letter in letters:
            self.store_stroke(letter, stroke)

    def process(self):
        local_data_storage = deepcopy(self.incoming_data)
        self.incoming_data = []

        for data in local_data_storage:
            if self.previous_time is None:
                self.previous_time = data[0]
                continue

            data[0], self.previous_time = data[0] - self.previous_time, data[0]

            if data[0] < MAX_DATA_TIMELAPSE:
                self.imu.calc(data)
                gyro = np.linalg.norm(np.array([data[7:]]))
                accel = np.linalg.norm(np.array([data[:3]]))

                accel = self.acceleration_filter.set_input(accel, data[0])

                if accel > ACCELERATION_RESET:
                    self.execute_spell()

                Yr = self.imu.get_y_direction()
                self.stroke.set_data(Yr, gyro)

    def execute_spell(self):
        self.out.setText('')

    def get_data(self):
        try:
            self.data_buffer += self.serial.read(self.serial.inWaiting())
            if self.data_buffer == '':
                return
            data_pieces = self.data_buffer.split(BUFFER_DELIMITER)

            # Put incomplete piece back to the buffer
            self.data_buffer = data_pieces.pop(-1)

            # If there are no complete data pieces - return from function
            if not data_pieces:
                return

            # Else - get the last of the pieces and discard the rest
            line = data_pieces[-1]

            result = [float(d) for d in line.split()]
            if len(result) != 9:
                raise ValueError('Nine pieces of data should be provided.')
            new_line = [time()] + result
            self.incoming_data.append(new_line)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Something went wrong... nobody cares.
            print e


if __name__ == '__main__':
    app = QApplication(sys.argv)
    listener = Listener(CORE_FILENAME)
    listener.show()
    sys.exit(app.exec_())
