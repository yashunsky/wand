#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from stick_control.uart_reader import UartReader

if __name__ == '__main__':
    reader = UartReader()
    timers = {}
    prev_output = ''
    for raw_data in reader():
        device_id = raw_data['device_id']
        delta = raw_data['delta']
        timers[device_id] = timers.get(device_id, 0) + delta

        output = '   '.join(['%d: %3.0f' % (id, value)
                             for id, value in timers.items()])
        if output != prev_output:
            print(output)
            prev_output = output
