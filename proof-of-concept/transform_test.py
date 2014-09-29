#! /usr/bin/env python

import numpy as np

Yr = np.array([1., 2., 1.])
y = np.array([Yr[0], Yr[1], 0])
y /= np.linalg.norm(y)

z = np.array([0., 0., 1.])

x = np.cross(y,z)
x /= np.linalg.norm(x)

M = np.matrix(np.vstack((x,y,z)))

Yt = np.array([Yr]).T

r = M*Yt
print r
print r[0,0], r[1, 0], r[2, 0]