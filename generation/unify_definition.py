#! /usr/bin/env python2.7

import numpy as np


def unify_stroke(stroke, points_count):

    s_delta = np.diff(stroke, axis=0)
    s_length = np.sqrt(s_delta[:, 0] ** 2 + s_delta[:, 1] ** 2)

    stroke_lengths = np.cumsum(s_length)

    stroke_lengths = np.hstack((np.array(0), stroke_lengths))

    out_division = np.linspace(0, stroke_lengths[-1], points_count)

    new_stroke = np.zeros((points_count, stroke.shape[1]))

    new_stroke[0] = stroke[0]
    new_stroke[-1] = stroke[-1]

    for p_id, div_point in enumerate(out_division[1:-1]):
        right_id = np.nonzero(stroke_lengths >= div_point)[0][0]
        left_id = right_id - 1
        offset = div_point - stroke_lengths[left_id]
        try:
            coeff = offset / s_length[left_id]
        except IndexError:
            coeff = 0

        pl = stroke[left_id]
        pr = stroke[right_id]

        p = pl + (pr - pl) * coeff
        new_stroke[p_id + 1] = p

    return new_stroke


def check_stroke(stroke, description_, offset):
    if not isinstance(description_, np.ndarray):
        description = np.array(description_)
    else:
        description = np.copy(description_)

    delta = stroke - description[:, :-1]
    radius = np.linalg.norm(delta, axis=1)

    return np.max(radius / (description[:, -1] * (1. + offset)))


def get_letter(stroke, segmentation, letters, offset):
    u_st = unify_stroke(stroke, segmentation)

    result = [(key, check_stroke(u_st, letter, offset))
              for key, letter in letters.items()]

    result.sort(key=lambda x: x[1])

    return result
