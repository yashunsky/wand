#!/usr/bin/env python3
# -*- coding: utf-8 -*-

TIME_SCALE = 0.001  # s/digit
TIME_STAMP_RANGE = 65536

if __name__ == '__main__':
    with open('raw.txt') as f:
        data = f.readlines()
    parts = [l.split(';') for l in data if l]
    tss = [(int(v[0]), int(v[1])) for v in parts]

    prev_timestamp = [None, None]

    deltas = [[], []]

    first = [None, None]
    last = [None, None]
    cycles = [0, 0]

    for ts in tss:
        device_id, time_stamp = ts

        if prev_timestamp[device_id] is not None and prev_timestamp[device_id] > time_stamp:
            print('device_id', device_id, 'was', prev_timestamp[device_id], 'now', time_stamp)

        prev_timestamp[device_id] = time_stamp
