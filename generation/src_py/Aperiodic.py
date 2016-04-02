#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''Aperiodic filter'''

class AperiodicFilter(object):
    """docstring for AperiodicFilter"""
    def __init__(self, T, output=None):
        super(AperiodicFilter, self).__init__()
        self.output = output
        self.T = T

    def set_input(self, value, step=1.0):
        if self.output is None:
            self.output = value
        else:    
            self.output = self.output + (value - self.output) * step / self.T
        return self.output

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    ap = AperiodicFilter(0.5, 0)
    points = [0] + [ap.set_input(1, 0.1) for i in xrange(100)]
    plt.plot(points)
    plt.show()
