#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import numpy as np

SOURCE_FILE = 'tetra_v2.txt'
DESTINATION = 'mirror_x.txt'

def to_arrays(input_dict):
    return {key: np.array(points)
                       for key, points in input_dict.items()}

def to_lists(input_dict):
    return {key: points.tolist()
                       for key, points in input_dict.items()}

def add_invertion(input_list, axis):
    add_on = []
    for letter in input_list:
        new_letter = letter[:, :]
        new_letter[:, axis] *= -1
        add_on.append(new_letter)
    input_list += add_on

def mirror_core(source, destination, x=True, z=False):
    with open(source, 'r') as source_file:
        core = json.load(source_file)
    core['letters'] = to_arrays(core['letters'])

    letters = core['letters'].values()
    if x:
        add_invertion(letters, 0)

    if z:
        add_invertion(letters, 2)

    core['letters'] = {'%s' % l_id : points for l_id, points in enumerate(letters)}

    core['letters'] = to_lists(core['letters'])

    with open(destination, 'w') as destination_file:
        json.dump(core, destination_file)


if __name__ == '__main__':
    mirror_core(SOURCE_FILE, DESTINATION)