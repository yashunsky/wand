#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4.QtGui import QApplication, QPushButton, QLineEdit, QGridLayout, QWidget

from stroke_widget import StrokeWidget

import sys

from os.path import join, isfile
from os import listdir

import numpy as np

from time import time


class StrokeViewer(StrokeWidget):
    """docstring for StrokeViewer"""
    def __init__(self):
        super(StrokeViewer, self).__init__()
        self.control_line = QWidget(self)
        self.gridLayout.addWidget(self.control_line, 1, 0, 1, 1)

        self.cl_grid = QGridLayout(self.control_line)

        self.prev_btn = QPushButton()
        self.prev_btn.setText('<')
        self.cl_grid.addWidget(self.prev_btn, 0, 0, 1, 1)

        self.name_edit = QLineEdit()
        self.cl_grid.addWidget(self.name_edit, 0, 1, 1, 1)

        self.confirm_btn = QPushButton()
        self.confirm_btn.setText('ok')
        self.cl_grid.addWidget(self.confirm_btn, 0, 2, 1, 1)

        self.next_btn = QPushButton()
        self.next_btn.setText('>')
        self.cl_grid.addWidget(self.next_btn, 0, 3, 1, 1)

        self.strokes = []

        self.out_path = 'letters'

        self.s_id = 0

        self.next_btn.clicked.connect(self.inc_id)

        self.prev_btn.clicked.connect(self.dec_id)

        self.confirm_btn.clicked.connect(self.classify)

    def classify(self):
        filename = '%s%.0f.txt' % (self.name_edit.text(), time())
        with open(join(self.out_path, filename), 'w') as f:
            np.savetxt(f, self.strokes[self.s_id]['data'])

    def inc_id(self):
        self.s_id = (self.s_id + 1) % len(self.strokes)
        self.set_stroke()

    def dec_id(self):
        self.s_id = (self.s_id - 1) % len(self.strokes)
        self.set_stroke()
        
    def set_source(self, path):
        files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

        self.strokes = [{'key': '', 'data': np.loadtxt(filename)} for filename in files]

        if len(self.strokes):
            self.s_id = 0
            self.set_stroke()

    def set_stroke(self):
        self.reset_stroke()

        new_stroke = self.strokes[self.s_id]['data']

        for point in new_stroke:
            if point.size == 3:
                self.set_coords_stereo(point)

if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    win = StrokeViewer()

    win.show()

    win.set_source('new_basis')

    sys.exit(app.exec_())