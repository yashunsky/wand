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

def tangent_circle(center, radius, segmentation=128):
    y = center #np.array([center]).T
    x = np.array([y[1], -y[0], 0])
    x = x/np.linalg.norm(x)
    z = np.cross(x, y)
    m = np.matrix(np.vstack((x, y, z)))

    circle = []
    for i in xrange(segmentation+1):
        a = i*2*np.pi/segmentation
        x = radius*np.cos(a)
        z = radius*np.sin(a)
        point = np.matrix([[x, 0, z]]).T
        point = m*point + np.matrix(center).T
        circle.append(np.array(point.T)[0])
    
    circle = np.array(circle)
    return circle

    return None

def stereographic(x, y, z):
    '''Transform 3D coords into 2D
    using stereographic projection'''
    return x/(1+y), -z/(1+y)

def make_cross(point, size=0.1):
    x, y = point
    l = np.array([x-size, y-size])
    t = np.array([x-size, y+size])
    r = np.array([x+size, y+size])
    b = np.array([x+size, y-size])
    return np.array([l, r, point, t, b, point])

class StrokeWidget(QWidget):
    """docstring for StrokeWidget"""
    def __init__(self):
        super(StrokeWidget, self).__init__()
        self.resize(512, 512)



        self.gridLayout = QGridLayout(self)
        self.pw = pg.PlotWidget(name='st', background='w') 

        self.circle = pg.PlotCurveItem(np.array([0]), np.array([0]), pen=pg.mkPen(width=2, color='m'))
        self.pw.addItem(self.circle)

        self.bg_stroke = pg.PlotCurveItem(np.array([0]), np.array([0]), pen=pg.mkPen(width=5, color='k'))
        self.pw.addItem(self.bg_stroke)

        self.stroke = pg.PlotCurveItem(np.array([0]), np.array([0]), pen=pg.mkPen(width=5, color='k'))
        self.pw.addItem(self.stroke)



        self.gridLayout.addWidget(self.pw, 0, 0, 1, 1)

        self.pw.getViewBox().setXRange(-np.pi, np.pi)
        self.pw.getViewBox().setYRange(-np.pi/2, np.pi/2)
        self.pw.getViewBox().setAspectLocked()

        self.stroke_data = np.array(())

    def set_background(self, path, letter, color='r', add_circles=False):
        with open(path, 'r') as f:
            data = json.load(f)
        letters_list = data['letters']
        circles = np.array([])
        if letter in letters_list:
            st = np.array(letters_list[letter])

            x = st[:, 0]
            y = st[:, 1]
            z = st[:, 2]

            if add_circles:
                for row in st:
                    circle = tangent_circle(row[:3], row[3])
                    if circles.size==0:
                        circles = circle
                    else:
                        circles = np.vstack((circles, circle))
        else:
            x = y = z = np.array([0])

        x, y = stereographic(x, y, z)
        cross = make_cross(np.array([x[0], y[0]]))
        x = np.hstack((cross[:, 0], x))
        y = np.hstack((cross[:, 1], y))

        self.bg_stroke.setData(x=x, y=y, pen=pg.mkPen(width=5, color=color))

        if not circles.size==0:
            x = circles[:, 0]
            y = circles[:, 1]
            z = circles[:, 2]
            x, y = stereographic(x, y, z)
            self.circle.setData(x=x, y=y, pen=pg.mkPen(width=0.5, color='b'))            

    def set_coords_3D(self, d):
        self.set_coords(d[0, 0], d[0, 2])

    def set_coords(self, x, y):
        new_point = np.array([x, y])
        if self.stroke_data.size == 0:
            self.stroke_data = make_cross(new_point)
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

    sw.set_background('mirror_x.txt', '7', add_circles=False)

    sw.show()

    sys.exit(app.exec_())    