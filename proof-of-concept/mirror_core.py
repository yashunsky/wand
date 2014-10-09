#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import numpy as np

SOURCE_FILE = 'tetra_v2.txt'
DESTINATION = 'mirror_x.txt'

def to_lists(input_dict):
    return {key: np.array(points)
                       for key, points in input_dict.items()}

def to_arrays(input_dict):
    return {key: points.tolist()
                       for key, points in input_dict.items()}


def mirror_core(source, destination, x=True, z=False, xz=False):
    with open(source, 'r') as source_file:
        core = json.load(source_file)
    core['letters'] = {key: np.array(points)
                       for key, points in core['letters'].items()}

if __name__ == '__main__':
    mirror_core(SOURCE_FILE, DESTINATION)