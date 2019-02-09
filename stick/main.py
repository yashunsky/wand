#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from uart_reader import UartReader
from setup import PORT, OFFSETS
from raw_processor import RawToSequence
from spells import ALL_SPELLS, ALL_PREFIXES


def process_sequence(state):
    str_sequence = ''.join(state['sequence'])
    if str_sequence in ALL_PREFIXES:
        if state['done']:
            return {'spell': ALL_SPELLS.get(str_sequence)}
        else:
            return {'vibro': len(state['sequence'])}
    return {}


if __name__ == '__main__':
    raw_stream = UartReader(serial_port=PORT)

    raw_processors = {device_id: RawToSequence(offsets['A'], offsets['G'])
                      for device_id, offsets in OFFSETS.items()}

    prev_sequence = []

    for raw_data in raw_stream():
        raw_to_sequence = raw_processors[raw_data['device_id']]
        state = raw_to_sequence(raw_data)

        if state['done'] or (state['sequence'] and
                             (state['sequence'] != prev_sequence)):
            print(state['sequence'], process_sequence(state))
        prev_sequence = state['sequence']
