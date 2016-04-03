#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json
import unittest

from src_py.pipe_state_machine import GenerationStateMachine
from src_py.pipe_state_machine import MODE_DEMO, MODE_RUN


INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'test_knowledge.json'

EPSILON = 0.00001


def almoste_equal(a, b):
    return a == b == 0 or almoste_zero(1 - a / b)


def almoste_zero(value):
    return abs(value) < EPSILON


def input_generator():
    with open(INPUT_LOG, 'r') as f:
        for line in f:
            data = map(float, line.split())
            yield {'delta': data[0],
                   'acc': data[1:4],
                   'mag': data[4:7],
                   'gyro': data[7:10]}


class CheckStateMachine(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CheckStateMachine, self).__init__(*args, **kwargs)
        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

    def decode_state(self, state):
        def get_key_by_value(value, source):
            for k, v in source.items():
                if v == value:
                    return k

        state_name = get_key_by_value(state, self.knowledge['states'])

        if 'demo_' in state_name:
            return self.knowledge['stroke_names'][state_name[5:]]

        return state_name

    def _test_mode_demo(self):

        state_machine = GenerationStateMachine(self.knowledge, MODE_DEMO)

        state = None

        for input_data in input_generator():
            new_state = state_machine(input_data)
            if new_state != state:
                state = new_state
                print self.decode_state(new_state)

    def test_mode_run(self):

        state_machine = GenerationStateMachine(self.knowledge, MODE_RUN)

        state = None

        for input_data in input_generator():
            new_state = state_machine(input_data)
            if new_state != state:
                state = new_state
                print self.decode_state(new_state)


if __name__ == '__main__':
    unittest.main()
