#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pyqtgraph.opengl as gl
import numpy as np


def show_strokes_3d(key,strokes, mean_stroke):
    view = gl.GLViewWidget()

    view.orbit(75, -15)
    view.show()
    # view.readQImage().save('%s-r.png'%key)
    # view.setBackgroundColor([255, 255, 255, 0])
    ## create three grids, add each to the view
    # xgrid = gl.GLGridItem(color=(0,0,0,255))
    # ygrid = gl.GLGridItem()
    zgrid = gl.GLGridItem()

    color = np.array([0, 0, 1, 0.5])
    for stroke in strokes:
        pos = stroke['data']

        colors = np.tile(color, (pos.shape[0], 1))

        line = gl.GLLinePlotItem(pos=pos, color=colors, width=5)
        view.addItem(line)

    color = np.array([1, 0, 0, 1])
    pos = mean_stroke[:, :3]
    colors = np.tile(color, (pos.shape[0], 1))
    line = gl.GLLinePlotItem(pos=pos, color=colors, width=10)
    view.addItem(line)

    # view.addItem(xgrid)
    # view.addItem(ygrid)
    view.addItem(zgrid)

    ## rotate x and y grids to face the correct direction
    # xgrid.rotate(90, 0, 1, 0)
    # ygrid.rotate(90, 1, 0, 0)

