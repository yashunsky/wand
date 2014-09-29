#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PySide.QtGui import QWidget, QApplication, QGridLayout
from PySide.QtGui import QVBoxLayout
from PySide.QtCore import QTimer

import pyqtgraph as pg
import numpy as np

import sys

import json

from time import time

from unify_definition import unify_stroke

class TouchSensor(QWidget):
    """docstring for TouchSensor"""
    def __init__(self, event_reciever):
        super(TouchSensor, self).__init__()
        self.set_coords = event_reciever.set_coords
        self.reset_stroke = event_reciever.reset_stroke
        self.analize_stroke = event_reciever.analize_stroke
        
    def mouseMoveEvent(self, event):
        super(TouchSensor, self).mouseMoveEvent(event)
        x = (float(event.x())/self.width()-0.5)*np.pi*2
        y = -(float(event.y())/self.height()-0.5)*np.pi
        self.set_coords(x, y)

    def mousePressEvent(self, event):
        super(TouchSensor, self).mousePressEvent(event)
        self.reset_stroke()

    def mouseReleaseEvent(self, event):
        super(TouchSensor, self).mouseReleaseEvent(event)
        self.analize_stroke()



class StrokeWidget(QWidget):
    """docstring for StrokeWidget"""
    def __init__(self):
        super(StrokeWidget, self).__init__()
        self.resize(512, 512)



        self.gridLayout = QGridLayout(self)
        self.pw = pg.PlotWidget(name='st', background='w') 

        self.bg_stroke = pg.PlotCurveItem(np.array([0]), np.array([0]), pen=pg.mkPen(width=5, color='k'))
        self.pw.addItem(self.bg_stroke)

        self.stroke = pg.PlotCurveItem(np.array([0]), np.array([0]), pen=pg.mkPen(width=5, color='k'))
        self.pw.addItem(self.stroke)

        self.gridLayout.addWidget(self.pw, 0, 0, 1, 1)

        self.pw.getViewBox().setXRange(-np.pi, np.pi)
        self.pw.getViewBox().setYRange(-np.pi/2, np.pi/2)
        self.pw.getViewBox().setAspectLocked()


        #self.pw.hideAxis('left')
        #self.pw.hideAxis('bottom')
        
        #self.touch = TouchSensor(self)

        #self.gridLayout.addWidget(self.touch, 0, 0, 1, 1)

        self.stroke_data = np.array(())

    def set_background(self, path, letter, color='r'):
        with open(path, 'r') as f:
            data = json.load(f)
        letters_list = data['letters']
        if letter in letters_list:
            st = np.array(letters_list[letter])

            x = st[:, 0]
            y = st[:, 1]
            z = st[:, 2]
        else:
            x = y = z = np.array([0])

        self.bg_stroke.setData(x=x/(1+y), y=-z/(1+y), pen=pg.mkPen(width=5, color=color))

    def set_coords_3D(self, d):
        self.set_coords(d[0, 0], d[0, 2])

    def set_coords(self, x, y):
        new_point = np.array([x, y])
        if self.stroke_data.size == 0:
            l = np.array([x-0.1, y])
            t = np.array([x, y+0.1])
            r = np.array([x+0.1, y])
            b = np.array([x, y-0.1])
            self.stroke_data = np.array([l, r, new_point, t, b, new_point])
        else:
            self.stroke_data = np.vstack((self.stroke_data, new_point))

        self.stroke.setData(x=self.stroke_data[:, 0], y=self.stroke_data[:, 1], pen=pg.mkPen(width=5, color='k'))
    
    def set_data(self, data):
        self.stroke_data = data
        if data.size > 0:
            self.stroke.setData(x=self.stroke_data[:, 0], y=self.stroke_data[:, 1], pen=pg.mkPen(width=5, color='k'))
        else:
            self.stroke.setData()

    def reset_stroke(self):
        self.stroke_data = np.array(())
        self.stroke.setData()

    def analize_stroke(self):
        u_st = unify_stroke(self.stroke_data,32)
        self.stroke.setData(x=u_st[:, 0], y=u_st[:, 1], pen=pg.mkPen(width=5, color='r'))

    def set_coords_stereo(self, point):
        sx, sy, sz = point
        sy = 0 if sy == -1 else sy 
        x, z = sx/(1+sy), -sz/(1+sy)

        self.set_coords(x, z)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    sw = StrokeWidget()

    sw.show()

    sys.exit(app.exec_())    