#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep

from knowledge.setup import OFFSETS, ACC_SCALE, G_CONST
import utils.tiny_numpy as np

INJECTION_INTERVAL = 0.05

PSEDO_POSITIONS = {
    'Z': (0, -1, 0),
    'Au': (0, -1, 1),
    'As': (-1, -1, 0),
    'Ad': (0, -1, -1),
    'Hu': (0, 0, 1),
    'Hs': (1, 0, 0),
    'Hd': (0, 0, -1),
    'Du': (0, 1, 1),
    'Ds': (-1, 1, 0),
    'Dd': (0, 1, -1),
    'N': (0, 1, 0)
}


class Snapshot(object):
    def __init__(self, device_id):
        super(Snapshot, self).__init__()
        self.device_id = device_id
        self.acc = None
        self.button_pressed = False
        self.gyro = OFFSETS[self.device_id]['G']

        self.set_expected_position('Hs', button=False)

    def set_expected_position(self, position, button=True):
        if position == 'release':
            self.button_pressed = False
            return

        acc = np.array(PSEDO_POSITIONS[position])
        acc /= (np.linalg.norm(acc) * ACC_SCALE / G_CONST)
        acc += OFFSETS[self.device_id]['A']

        self.acc = acc
        self.button_pressed = button

    def set_feedback(self, state):
        if state['spell'] is not None or state['failed']:
            self.button_pressed = False

    def get_sensor_data(self):
        return {'device_id': self.device_id,
                'button': int(self.button_pressed),
                'gyro': self.gyro,
                'acc': self.acc}


class DataInjector(object):
    def __init__(self, ids=[]):
        super(DataInjector, self).__init__()
        self.snapshots = {}
        self.ids = ids
        for id in ids:
            self.init_device(id)
        self.in_loop = False

    def init_device(self, device_id):
        self.snapshots[device_id] = Snapshot(device_id)

    def get_snapshot(self, device_id):
        if device_id not in self.snapshots:
            self.snapshots[device_id] = Snapshot(device_id)
        return self.snapshots[device_id]

    def set_position(self, device_id, position):
        if device_id in self.ids:
            self.get_snapshot(device_id).set_expected_position(position)

    def set_inner_feedback(self, device_id, state):
        self.get_snapshot(device_id).set_feedback(state)

    def __call__(self):
        self.in_loop = True

        while self.in_loop:
            sleep(INJECTION_INTERVAL)
            for snapshot in self.snapshots.values():
                data = snapshot.get_sensor_data()
                data['delta'] = INJECTION_INTERVAL
                yield data
            else:
                yield None

    def process_action(self, message):
        action = message['action']
        if action == 'exit':
            self.in_loop = False
        elif action == 'position':
            self.set_position(message['device_id'],
                              message['position'])
