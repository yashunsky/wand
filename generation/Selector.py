#! /usr/bin/env python

import numpy as np

from unify_definition import get_letter

import json


class Selector(object):
    def __init__(self, path):

        self.letters_dict = {}

        with open(path, 'r') as f:
            data = json.load(f)
            letters_lists = data['letters']
            for key, item in letters_lists.items():
                self.letters_dict[key] = np.array(item)
            self.segmentation = data['segmentation']

    def check_stroke(self, stroke):
        letters = get_letter(stroke, self.segmentation, self.letters_dict)
        return letters
