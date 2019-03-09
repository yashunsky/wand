#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from time import time
from stick_control.uart_reader import UartReader

if __name__ == '__main__':
    reader = UartReader()
    timers = {}
    tss = {}
    prev_ts = 0
    start = time()
    for raw_data in reader():
        device_id = raw_data['device_id']
        delta = raw_data['delta']
        timers[device_id] = timers.get(device_id, 0) + delta

        old_tss = tss.get(device_id, 0)
        if old_tss > raw_data['timestamp']:
            print('New timer value %d is lower then previous %d on device %d' %
                  (raw_data['timestamp'], old_tss, device_id))
        tss[device_id] = raw_data['timestamp']

        ts = int(time() - start)

        timers_str = '   '.join(['%d: %3.0f' % (id, value)
                                 for id, value in timers.items()])

        timestamps_str = '   '.join(['%d: %3.0f' % (id, value)
                                     for id, value in tss.items()])

        output = '%d %s %s' % (ts, timers_str, timestamps_str)

        if ts != prev_ts:
            print(output)
            prev_ts = ts
