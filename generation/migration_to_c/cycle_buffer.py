#! /usr/bin/env python2.7

from math import sin, pi
import matplotlib.pyplot as plt


INPUT_LENGTH = 100
BUFFER_LENGTH = 30


def input_generator():
    for x in xrange(INPUT_LENGTH):
        a = sin(pi * (x - 10) / 20)
        yield 0 if a < 0 else a


class CycleBuffer(object):
    def __init__(self):
        super(CycleBuffer, self).__init__()

        self.py = [0] * BUFFER_LENGTH

        self.c = [0] * BUFFER_LENGTH
        self.c_index = 0

    def update(self, value):
        self.update_py(value)
        self.update_c(value)

        return self.get_py(), self.get_c()

    def update_py(self, value):
        self.py = (self.py + [value])[1:]

    def update_c(self, value):
        self.c[self.c_index] = value
        self.c_index = (self.c_index + 1) % BUFFER_LENGTH

    def get_py(self):
        return self.py

    def get_c(self):
        return self.c[self.c_index:] + self.c[:self.c_index]

if __name__ == '__main__':
    buf = CycleBuffer()

    for index, x in enumerate(input_generator()):
        py, c = buf.update(x)
        if index % 19 == 0:
            plt.subplot(211)
            plt.plot(py, '.-')
            plt.subplot(212)
            plt.plot(c, '.-')

            plt.show()
