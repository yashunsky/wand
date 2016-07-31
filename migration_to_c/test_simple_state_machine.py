#!/usr/bin/env python

import json

from src_py.input_generator import InputGenerator
from src_py.simple_state_machine import StateMachine as SM_PY
from src_py.simple_state_machine import OUTPUT_TEST
from simple_state_machine import StateMachine as SM_C


INPUT_LOG = 'test_input.log'
KNOWLEDGE = 'test_knowledge.json'

if __name__ == '__main__':
    with open(KNOWLEDGE, 'r') as f:
        knowledge = json.load(f)

    state_names = {value: key for key, value in knowledge['states'].items()}
    splitter_state_names = {value: key for key, value in
                            knowledge['splitting']['states'].items()}

    input_generator = InputGenerator()

    state_machine = SM_C(knowledge)

    all_strokes = knowledge['strokes'].keys()

    prev_state = None

    for input_data in input_generator(False, INPUT_LOG, False):
        new_state = state_machine(input_data, all_strokes)
        if prev_state != new_state:
            prev_state = new_state
            print state_names[new_state]
