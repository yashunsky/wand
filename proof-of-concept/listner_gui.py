#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PySide.QtGui import QApplication, QWidget, QLabel, QTextEdit, QGridLayout
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


class Listner(QWidget):
    """docstring for Listner"""
    def __init__(self):
        super(Listner, self).__init__()
        self.resize(500, 500)
        self.out = QTextEdit(self)
        self.grid = QGridLayout(self)
        self.display = StrokeWidget()
        self.grid.addWidget(self.display, 0, 0, 1, 1)
        self.grid.addWidget(self.out, 1, 0, 1, 1)
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

        self.im = IMU()
        self.st = Stroke()
        self.st.widget = self.display

        self.prev = None

        self.data_buffer = ''

    def process(self):
        # if self.log:
        #     to_print = '%s' % len(self.log)
        # else:
        #     to_print = 'noting yet'

        # to_print = '%.1f' % (time()%100)
        # self.out.setText(to_print)


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

#            print (self.im.pitch, self.im.roll, self.im.yaw)



        pitch = self.im.pitch
        roll = self.im.roll
        yaw = self.im.yaw

        #to_print = '%.1f %.1f %.1f' % (self.im.pitch, self.im.roll, self.im.yaw)
        #self.out.setText(to_print)
        
        gyro = np.array([data[7:]])
        
        Xr=(cos(pitch)*cos(yaw),-cos(pitch)*sin(yaw),sin(pitch)) 
        Zr=(sin(roll)*sin(yaw)+cos(roll)*sin(pitch)*cos(yaw),sin(roll)*cos(yaw)-cos(roll)*sin(pitch)*sin(yaw),-cos(roll)*cos(pitch))

        Yr = (-Xr[1]*Zr[2]+Zr[1]*Xr[2],
              -Zr[0]*Xr[2]+Xr[0]*Zr[2],
              -Xr[0]*Zr[1]+Xr[1]*Zr[0])

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
            
            
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print e





if __name__ == '__main__':
    app = QApplication(sys.argv)

    ls = Listner()

    ls.show()

    sys.exit(app.exec_())