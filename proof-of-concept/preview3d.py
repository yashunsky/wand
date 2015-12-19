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

    # color = np.array([0, 0, 1, 0.2])
    # for stroke in strokes:
    #     pos = stroke['data']

    #     colors = np.tile(color, (pos.shape[0], 1))

    #     line = gl.GLLinePlotItem(pos=pos, color=colors, width=5)
    #     view.addItem(line)


    pos = mean_stroke[:, :3]

    color1 = np.array([0, 1, 0, 1])
    color2 = np.array([1, 0, 0, 1])

    steps = np.linspace(0, 1, pos.shape[0])

    R = np.interp(steps, np.array([0, 1]), np.array([color1[0], color2[0]]))
    G = np.interp(steps, np.array([0, 1]), np.array([color1[1], color2[1]]))
    B = np.interp(steps, np.array([0, 1]), np.array([color1[2], color2[2]]))
    A = np.interp(steps, np.array([0, 1]), np.array([color1[3], color2[3]]))

    colors = np.vstack((R, G, B, A)).T

    line = gl.GLLinePlotItem(pos=pos, color=colors, width=40, mode='line_strip')
    view.addItem(line)

    # view.addItem(xgrid)
    # view.addItem(ygrid)
    view.addItem(zgrid)

    ## rotate x and y grids to face the correct direction
    # xgrid.rotate(90, 0, 1, 0)
    # ygrid.rotate(90, 1, 0, 0)

    print 'var geometry = new THREE.Geometry();\ngeometry.vertices.push(\n'
    for point in pos:
        print 'new THREE.Vector3(%f, %f, %f),' % (point[0], point[1], point[2])
    print ');\ngeometry.colors.push(\n'
    for color in colors:
        hexc = hex(int(color[0]*255)*65536+
       int(color[1]*255)*256+
       int(color[2]*255))

        print 'new THREE.Color( %s ),' % hexc
    print ');'
