#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SequenceProcessor(object):
    def __init__(self, sequences):
        super(SequenceProcessor, self).__init__()

        self.dictionary = sequences['dictionary']

        self.sequence = []

        self.init_stroke = sequences['init_stroke']

        self.states = sequences['states']

        self.compare_limit = sequences['compare_limit']

    def get_next_strokes(self):
        s_length = len(self.sequence)

        result = set([seq[s_length - 1] for seq in self.dictionary
                     if seq[:s_length - 1] == self.sequence[1:]])

        return result if s_length else set()

    def next_step(self, strokes, accessible, is_idle):
        if is_idle:
            self.sequence = []

        next_strokes = self.get_next_strokes() & set(accessible)

        next = self.choose_best(strokes, next_strokes)
        if next:
            if next == self.init_stroke:
                self.sequence = [self.init_stroke]
                return self.states['in_progress_0']

            self.sequence += [next]
            key = self.sequence[1:]

            try:
                result = self.states['done_sequence_%i' %
                                     self.dictionary.index(key)]
            except ValueError:
                pass
            else:
                self.sequence = []
                return result

            return self.states['in_progress_%i' % (len(self.sequence) - 1)]

        return self.states['unsupported']

    def choose_best(self, strokes, accessible):
        result = strokes[0][0]
        if (strokes[0][1] != 0 and
           strokes[1][1] / strokes[0][1] < self.compare_limit):
            result = None

        return (result if result in accessible or
                result == self.init_stroke else None)
