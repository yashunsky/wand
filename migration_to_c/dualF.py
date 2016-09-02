#!/usr/bin/python

import select
import sys

import json

from src_py.input_generator import InputGenerator as Ig
from c_wrap import set_fsm_data

KNOWLEDGE = 'generation_knowledge.json'

COLORS = ([0, 0, 0],  # BLANK,
          [255, 255, 255],  # WHITE,
          [255, 0, 0],  # RED,
          [100, 100, 0],  # ORANGE,
          [255, 255, 0],  # YELLOW,
          [0, 255, 0],  # GREEN,
          [255, 0, 255],  # VIOLET
          [0, 0, 255])  # CALIBRATION


class DualFSM(object):

    def __init__(self):
        super(DualFSM, self).__init__()

        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

        self.input_generator = Ig(serial_port='/dev/tty.usbmodem1A1211',  # '/dev/tty.usbmodem1411',
                                  dual=True,
                                  gyro_remap=lambda g: [g[1], -g[0], g[2]])

        self.set_accessible()

    def set_accessible(self, accessible=[0, 1, 2, 3, 4, 5, 6, 7, 8]):
        self.access = sum([2 ** x for x in accessible])

    def run(self):
        for data in self.input_generator(True):
            device_id = data['device_id']

            color, blink_on, blink_off, vibro = set_fsm_data(device_id,
                                                             data['delta'],
                                                             data['acc'],
                                                             data['gyro'],
                                                             data['mag'],
                                                             self.access)

            feedback = tuple(COLORS[color] + [vibro, blink_on, blink_off])

            self.input_generator.set_feedback(device_id, feedback)

            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                self.input_generator.in_loop = False
        print 'that\'s all'

if __name__ == '__main__':
    dsm = DualFSM()
    dsm.run()
