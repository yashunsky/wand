#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

from math import sqrt

from copy import copy

SEGMENTATION = 32
STROKE_MAX_LENGTH = 256


def get_segmentation():
    return SEGMENTATION


def get_stroke_max_length():
    return STROKE_MAX_LENGTH


def get_dist(a, b):
    delta = 0

    for j in xrange(3):
        d = a[j] - b[j]
        delta += d * d

    return sqrt(delta)


def unify_stroke(stroke, length):
    new_stroke = [[0.0, 0.0, 0.0]] * SEGMENTATION
    stroke_lengths = [0.0] * STROKE_MAX_LENGTH

    for i in xrange(1, length):
        stroke_lengths[i] = stroke_lengths[i - 1] + get_dist(stroke[i - 1],
                                                             stroke[i])

    step = stroke_lengths[length - 1] / (SEGMENTATION - 1)

    new_stroke[0] = copy(stroke[0])
    new_stroke[SEGMENTATION - 1] = copy(stroke[length - 1])

    new_stroke_id = 1
    next_length = step

    for i in xrange(1, length):
        if stroke_lengths[i] > next_length:
            p1 = stroke[i - 1]
            p2 = stroke[i]

            delta = stroke_lengths[i] - stroke_lengths[i - 1]

            coeff = (1 - ((stroke_lengths[i] - next_length) / delta)
                     if delta != 0 else 0)

            p_new = [0, 0, 0]

            for j in xrange(3):
                p_new[j] = p1[j] + (p2[j] - p1[j]) * coeff

            new_stroke[new_stroke_id] = copy(p_new)
            new_stroke_id += 1
            next_length += step
            if new_stroke_id == SEGMENTATION - 1:
                break

    return new_stroke


def check_stroke(stroke, description):
    errors = [0.0] * SEGMENTATION

    mean = 0.0

    result = 0.0

    for i in xrange(SEGMENTATION):
        radius = get_dist(stroke[i], description[i])

        radius -= description[i][3]

        radius = 0 if radius < 0 else radius

        errors[i] = radius

        mean += radius

    mean /= SEGMENTATION

    for i in xrange(SEGMENTATION):
        d = errors[i] - mean
        result += d * d

    return sqrt(result / SEGMENTATION)
