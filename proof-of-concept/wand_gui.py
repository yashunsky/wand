#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PySide.QtGui import QApplication, QWidget, QLabel, QTextEdit, QGridLayout, QComboBox
from PySide.QtCore import QTimer
from time import time
import sys
import serial

from IMU import IMU
from Stroke import Stroke
from Selector import Selector

import numpy as np
from math import sin, cos

from stroke_widget import StrokeWidget

from copy import deepcopy

from time import time


PLATFORM_SPECIFIC_QUOTIENTS = {
    'stm': ((744, -499, -491), (1857, 530, 426)),
    'arduino': ((-504, -615, -564), (597, 488, 384))
}

class Listner(QWidget):
    """docstring for Listner"""
    def __init__(self, core_file_name):
        super(Listner, self).__init__()
        self.core_file_name = core_file_name
        self.resize(500, 500)
        self.out = QTextEdit(self)
        self.grid = QGridLayout(self)
        self.display = StrokeWidget()
        self.selector = QComboBox()
        self.grid.addWidget(self.display, 0, 0, 1, 1)
        self.grid.addWidget(self.selector, 1, 0, 1, 1)
        # self.grid.addWidget(self.out, 2, 0, 1, 1)
        self.serial_timer = QTimer()
        self.serial_timer.setInterval(20)
        self.serial_timer.timeout.connect(self.get_data)
        self.serial_timer.start()

        self.process_timer = QTimer()
        self.process_timer.setInterval(100)
        self.process_timer.timeout.connect(self.process)
        self.process_timer.start()

        port = "/dev/ttyUSB0"
        self.ser = serial.Serial(port, 115200, timeout=0)
        self.log = []

        self.im = IMU(PLATFORM_SPECIFIC_QUOTIENTS['stm'])
        self.st = Stroke()
        self.sl = Selector(self.core_file_name)

        self.st.widget = self.display
        self.st.on_done = self.get_stroke

        self.prev = None

        self.data_buffer = ''

        self.init_selector()

        self.timer = QTimer()
        self.timer.timeout.connect(self.set_background)

    def init_selector(self):
        sel_lines = self.sl.letters_dict.keys()
        sel_lines.insert(0, 'free run')
        self.selector.addItems(sel_lines)
        self.selector.currentIndexChanged.connect(self.set_background)

    def set_background(self):
        letter = self.selector.currentText()
        self.display.set_background(self.core_file_name, letter)

    def get_stroke(self, stroke):
        #np.savetxt('new_basis/%.0f.txt' % time(), stroke)

        #return

        letters = self.sl.check_stroke(stroke)

        letter = self.selector.currentText()

        key = None

        if letter in letters:
            key = letter

        if letter == 'free run' and letters:
            key = letters[0]

        if key is not None:
            self.display.set_background(self.core_file_name, key, color='g')
            np.savetxt('learned/%s%.0f.txt' % (key, time()), stroke)
            self.timer.start(1000)

    def process(self):
        local_log = deepcopy(self.log)
        self.log = []

        data = [0]*10
        while local_log:
            data = local_log.pop(0)
            if self.prev is None:
                self.prev = data[0]
                continue

            data[0], self.prev = data[0]-self.prev, data[0]

            if data[0] < 0.05:
                self.im.calc(data)

                gyro = np.array([data[7:]])

                Yr = self.im.get_y_direction()

                self.st.set_data(Yr, np.linalg.norm(gyro))


    def get_data(self):
        line = ''

        try:

            self.data_buffer += self.ser.read(self.ser.inWaiting())

            if self.data_buffer == '':
                return

            breaked = self.data_buffer.split('\r\n')

            self.data_buffer = breaked[-1]

            if len(breaked) > 1:
                line = breaked[-2]
            else:
                return

            result = [float(d) for d in line.split()]

            if not len(result) == 9:
                return

            new_line = [time()] + result

            self.log.append(new_line)
            # with open('data.raw', 'a') as f:
            #    f.write(' '.join([str(d) for d in new_line])+'\n')


        except KeyboardInterrupt:
            raise
        except Exception as e:
            print e





if __name__ == '__main__':
    app = QApplication(sys.argv)

    ls = Listner('tetra_v2.txt')

    ls.show()

    sys.exit(app.exec_())