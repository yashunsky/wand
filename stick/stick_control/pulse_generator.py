#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep

INJECTION_INTERVAL = 0.05


class PulseGenerator(object):
    def __init__(self, ids=None):
        super(PulseGenerator, self).__init__()
        self.snapshots = [{'device_id': id, 'delta': INJECTION_INTERVAL}
                          for id in ids or []]

    def __call__(self):
        self.in_loop = True

        while self.in_loop:
            sleep(INJECTION_INTERVAL)
            for snapshot in self.snapshots:
                yield snapshot

    def stop(self):
        self.in_loop = False

    def process_action(self, message):
        action = message['action']
        if action == 'exit':
            self.stop()

    def set_feedback(self, device_id, vibro, r, g, b, w):
        pass
