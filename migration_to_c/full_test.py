#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import json
import unittest

from src_py.input_generator import InputGenerator
from src_py.state_machine import GenerationStateMachine as PyStateMachine
from src_py.state_machine import MODE_DEMO, MODE_RUN, OUTPUT_TEST

from state_machine import MigrationStateMachine as CStateMachine

from numpy import ndarray

INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'test_knowledge.json'

EPSILON = 0.0001


def almoste_equal(a, b):
    return a == b == 0 or almoste_zero(1 - a / b)


def almoste_zero(value):
    return abs(value) < EPSILON


def deep_almose_equal(a, b):
    if isinstance(a, dict):
        return all((deep_almose_equal(a[key], b[key]) for key in a))
    elif isinstance(a, str) or isinstance(a, unicode) or a is None:
        return a == b
    elif isinstance(a, tuple) or isinstance(a, list) or isinstance(a, ndarray):
        return all((deep_almose_equal(_a, _b) for _a, _b in zip(a, b)))
    else:
        return almoste_equal(a, b)


class CheckStateMachine(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CheckStateMachine, self).__init__(*args, **kwargs)
        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)
        self.input_generator = InputGenerator()

    def test_mode_demo(self):

        py_state_machine = PyStateMachine(self.knowledge, MODE_DEMO)
        c_state_machine = CStateMachine(self.knowledge, MODE_DEMO)

        for input_data in self.input_generator(False, INPUT_LOG, False):
            py_state = py_state_machine(input_data, OUTPUT_TEST)
            c_state = c_state_machine(input_data, OUTPUT_TEST)

            assert deep_almose_equal(py_state, c_state)

    def test_mode_run(self):

        py_state_machine = PyStateMachine(self.knowledge, MODE_RUN)
        c_state_machine = PyStateMachine(self.knowledge, MODE_RUN)

        for input_data in self.input_generator(False, INPUT_LOG, False):
            py_state = py_state_machine(input_data, OUTPUT_TEST)
            c_state = c_state_machine(input_data, OUTPUT_TEST)

            assert deep_almose_equal(py_state, c_state)


if __name__ == '__main__':
    unittest.main()
