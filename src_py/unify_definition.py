#! /usr/bin/env python2.7

import numpy as np


def unify_stroke(stroke, points_count):
    s_delta = np.diff(stroke, axis=0)
    s_length = np.linalg.norm(s_delta, axis=1)
    stroke_lengths = np.cumsum(s_length)

    stroke_lengths = np.hstack((np.array(0), stroke_lengths))

    new_stroke = np.zeros((points_count, stroke.shape[1]))

    new_stroke[0] = stroke[0]
    new_stroke[-1] = stroke[-1]

    step = stroke_lengths[-1] / (points_count - 1)

    next_length = step

    new_stroke_id = 1

    for i in xrange(len(stroke)):
        while (stroke_lengths[i] > next_length):
            p1 = stroke[i - 1]
            p2 = stroke[i]
            delta = stroke_lengths[i] - stroke_lengths[i - 1]
            coeff = (0 if delta == 0
                     else (1 - ((stroke_lengths[i] - next_length) / delta)))

            new_stroke[new_stroke_id] = p1 + (p2 - p1) * coeff
            new_stroke_id += 1
            next_length += step

    return new_stroke


def check_stroke(stroke, description_):
    if not isinstance(description_, np.ndarray):
        description = np.array(description_)
    else:
        description = np.copy(description_)

    delta = stroke - description
    error = np.linalg.norm(delta, axis=1)

    return np.std(error)


def get_letter(stroke, segmentation, letters):
    u_st = unify_stroke(stroke, segmentation)

    result = [(key, check_stroke(u_st, letter))
              for key, letter in letters.items()]

    result.sort(key=lambda x: x[1])

    return result
