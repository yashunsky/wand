#!/usr/bin/env python
#-*- coding: utf-8 -*-

from copy import deepcopy
import os
import serial
import sys
from time import time

import numpy as np
from PySide.QtGui import QApplication, QWidget, QTextEdit, QGridLayout, QComboBox
from PySide.QtCore import QTimer

from IMU import IMU
from Selector import Selector
from Stroke import Stroke
from stroke_widget import StrokeWidget


PLATFORM_SPECIFIC_QUOTIENTS = {
    'stm': ((744, -499, -491), (1857, 530, 426)),
    'arduino': ((-504, -615, -564), (597, 488, 384))
}
CORE_FILENAME = 'tetra_v2.txt'
LEARNED_FOLDER = 'learned'
MAX_DATA_TIMELAPSE = 0.05
BUFFER_DELIMITER = '\r\n'


class Listener(QWidget):
    def __init__(self, core_file_name):
        super(Listener, self).__init__()
        self.core_file_name = core_file_name
        self.resize(500, 500)
        self.out = QTextEdit(self)
        self.grid = QGridLayout(self)
        self.display = StrokeWidget()
        self.selector = QComboBox()
        self.grid.addWidget(self.display, 0, 0, 1, 1)
        self.grid.addWidget(self.selector, 1, 0, 1, 1)
        self.serial_timer = QTimer()
        self.serial_timer.setInterval(20)
        self.serial_timer.timeout.connect(self.get_data)
        self.serial_timer.start()

        self.process_timer = QTimer()
        self.process_timer.setInterval(100)
        self.process_timer.timeout.connect(self.process)
        self.process_timer.start()

        port = "/dev/ttyUSB0"
        self.serial = serial.Serial(port, 115200, timeout=0)
        self.incoming_data = []

        self.imu = IMU(PLATFORM_SPECIFIC_QUOTIENTS['stm'])
        self.stroke = Stroke()
        self.selector = Selector(self.core_file_name)

        self.stroke.widget = self.display
        self.stroke.on_done = self.get_stroke

        self.previous_time = None

        self.data_buffer = ''

        self.init_selector()

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_background)

    def init_selector(self):
        sel_lines = self.selector.letters_dict.keys()
        sel_lines.insert(0, 'free run')
        self.selector.addItems(sel_lines)
        self.selector.currentIndexChanged.connect(self.set_background)

    def set_background(self):
        letter = self.selector.currentText()
        self.display.set_background(self.core_file_name, letter)

    def store_stroke(self, key, stroke):
        self.display.set_background(self.core_file_name, key, color='g')
        file_name = '{key}{time}.txt'.format(key=key, time=int(time()))
        file_path = os.path.join(LEARNED_FOLDER, file_name)
        np.savetxt(file_path, stroke)
        self.timer.start(1000)

    def get_stroke(self, stroke):
        letters = self.selector.check_stroke(stroke)
        letter = self.selector.currentText()

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
                gyro = np.array([data[7:]])
                Yr = self.imu.get_y_direction()
                self.stroke.set_data(Yr, np.linalg.norm(gyro))

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
