#!/usr/bin/env python
#-*- coding: utf-8 -*-

from os.path import join, isfile, basename
from os import listdir

from unify_definition import unify_stroke

import numpy as np

import matplotlib.pyplot as plt

import pickle
import json

def get_letters(path):
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    letters = {}
    for f in files:
        data = np.loadtxt(f)
        key = basename(f)[0]
        if not key in letters:
            letters[key] = []
        letters[key].append(data)
    return letters

def make_core(letters, points):
    core = {}
    for key, letters_group in letters.items():
        unified = np.array([unify_stroke(letter, points) for letter in letters_group])

        centers = np.mean(unified, axis=0)

        R = []

        for u in unified:
            dists = u - centers
            radius = np.linalg.norm(dists, axis=1)
            R.append(radius)
            x = u[:, 0]
            y = u[:, 1]
            z = u[:, 2]
            plt.plot(x/(1+y), -z/(1+y), '.-.' )

        R = np.max(np.array(R), axis=0)

        core[key] = np.hstack((centers, np.array([R]).T))
        x = centers[:, 0]
        y = centers[:, 1]
        z = centers[:, 2]
        plt.plot(x/(1+y), -z/(1+y) , linewidth=5)
        #plt.show()
    return core

if __name__ == '__main__':
    letters = get_letters('letters')
    
    segmentation = 32
    core = make_core(letters, segmentation)
    dump_data = {'segmentation': segmentation}
    dump_data['letters'] = {key: data.tolist() for key, data in core.items()}
    with open('core.txt', 'w') as f:
        json.dump(dump_data, f, indent=1)