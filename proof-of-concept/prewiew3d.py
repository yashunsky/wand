#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4.QtGui import QApplication

import pyqtgraph as pg

import pyqtgraph.opengl as gl

import sys

import numpy as np

def show_strokes(strokes, mean_stroke):
    view = gl.GLViewWidget()
    view.show()
    # view.setBackgroundColor([100,0.7,0.7,1])
    ## create three grids, add each to the view
    # xgrid = gl.GLGridItem(color=(0,0,0,255))
    # ygrid = gl.GLGridItem()
    zgrid = gl.GLGridItem()

    line = gl.GLLinePlotItem(pos=np.array([[0,0,0], [1,1,1]]), color=np.array([[0.5, 1, 0.5, 0.5], [0.5, 1, 0.5, 0.5]]), width=5)
    view.addItem(line)

    # view.addItem(xgrid)
    # view.addItem(ygrid)
    view.addItem(zgrid)

    ## rotate x and y grids to face the correct direction
    # xgrid.rotate(90, 0, 1, 0)
    # ygrid.rotate(90, 1, 0, 0)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    show_strokes()

    sys.exit(app.exec_())