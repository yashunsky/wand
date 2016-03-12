#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SequenceProcessor(object):
    def __init__(self, init_word, dictionary):
        super(SequenceProcessor, self).__init__()

        self.dictionary = dictionary

        self.sequence = []

        self.init_word = init_word

    def get_next_words(self):
        s_length = len(self.sequence)
        return set([seq[s_length - 1] for seq in self.dictionary.keys()
                    if seq[:s_length - 1] == tuple(self.sequence[1:])])

    def next_step_chouse_best(self, words):
        next_words = self.get_next_words()

        for word in words:
            if word in next_words:
                self.sequence += [word]
                key = tuple(self.sequence[1:])
                if key in self.dictionary:
                    self.on_sequence_done(self.dictionary[key])
                    self.sequence = []

                return len(self.sequence)

        if self.init_word in words:
            self.sequence = [self.init_word]
            return 1

    def next_step(self, word):
        return self.next_step_chouse_best([word])

    def on_sequence_done(self, name):
        print 'done', name

if __name__ == '__main__':
    sp = SequenceProcessor('a',
                           {('b', 'c'): 1, ('c', 'b'): 2, ('b', 'd'): 4,
                            ('c', 'd'): 4, ('d', 'd'): 3, ('d', 'c'): 5})

    sp.next_step('c')
    sp.next_step('a')
    sp.next_step('b')
    sp.next_step('b')
    sp.next_step('b')
    sp.next_step('d')
    sp.next_step('a')
    sp.next_step_chouse_best(('b', 'c'))
    sp.next_step_chouse_best(('b', 'c'))
