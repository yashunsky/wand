#!/usr/bin/python

import select
import sys

import json

from src_py.input_generator import InputGenerator as Ig
from c_wrap import set_fsm_data

KNOWLEDGE = 'generation_knowledge.json'

COLORS = ((0, 0, 0),  # BLANK,
          (255, 255, 255),  # WHITE,
          (255, 0, 0),  # RED,
          (100, 100, 0),  # ORANGE,
          (255, 255, 0),  # YELLOW,
          (0, 255, 0),  # GREEN,
          (255, 0, 255),  # VIOLET
          (0, 0, 255))  # CALIBRATION


FEEDBACK = {'calibration': (100, 100, 0, 0),
            "done_0": (0, 0, 0, 30),
            "done_1": (0, 0, 0, 100),
            "done_2": (255, 255, 255, 65),
            "done_3": (255, 0, 0, 65),
            "done_4": (255, 255, 0, 65),
            "done_5": (255, 0, 255, 65),
            "done_6": (255, 255, 255, 65),
            "done_7": (255, 127, 0, 65),
            "done_8": (0, 255, 0, 65),
            'none': (10, 10, 10, 0)}


class DualFSM(object):

    def __init__(self):
        super(DualFSM, self).__init__()

        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

        self.input_generator = Ig(serial_port='/dev/tty.usbmodem1411',
                                  dual=True,
                                  gyro_remap=lambda g: [g[1], -g[0], g[2]])

        self.set_accessible()

    def set_accessible(self, accessible=[0, 1, 2, 3, 4, 5, 6, 7, 8]):
        self.access = sum([2 ** x for x in accessible])

    def run(self):
        for sensor_data in self.input_generator(True):
            device_id = sensor_data['device_id']

            if device_id == 1:
                continue

            color, blink, vibro = set_fsm_data(device_id,
                                               sensor_data['delta'],
                                               sensor_data['acc'],
                                               sensor_data['gyro'],
                                               sensor_data['mag'],
                                               self.access)

            feedback = tuple(list(COLORS[color]) + [vibro])

            self.input_generator.set_feedback(device_id, feedback)

            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                self.input_generator.in_loop = False
        print 'that\'s all'

if __name__ == '__main__':
    dsm = DualFSM()
    dsm.run()
