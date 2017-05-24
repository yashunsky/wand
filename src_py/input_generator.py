#!/usr/bin/env python
# -*- coding: utf8 -*-

import serial

from time import sleep

SERIAL_PORT = '/dev/tty.usbmodem1411'

BAUDE_RATE = 115200
BUFFER_DELIMITER = '\r'

TIME_SCALE = 0.001  # s/digit

TIME_STAMP_RANGE = 2 ** 32


class InputGenerator(object):
    def __init__(self, serial_port=SERIAL_PORT, dual=False,
                 gyro_remap=lambda x: x, baude_rate=BAUDE_RATE):
        super(InputGenerator, self).__init__()
        self.serial_port = serial_port
        self.dual = dual
        self.gyro_remap = gyro_remap
        self.baude_rate = baude_rate

        self.in_loop = False
        self.is_running = False

        self.prev_timestamp = [None, None]

        self.first_line = True

    def get_data(self):
        self.data_buffer += self.serial.read(self.serial.inWaiting())

        if self.data_buffer == '':
            return

        data_pieces = self.data_buffer.split(BUFFER_DELIMITER)

        # Put incomplete piece back to the buffer
        self.data_buffer = data_pieces.pop(-1)

        if not data_pieces:
            return

        for line in data_pieces:
            if self.first_line:
                self.first_line = False
            elif line:
                yield self.parse_line(line)

    def parse_line(self, line):
        data = [float(value) for value in line.split(';')]

        if self.dual:
            device_id = int(data[0])
            data = data[1:]
        else:
            device_id = 0

        time_stamp = data[0]

        delta = (0 if self.prev_timestamp[device_id] is None
                 else time_stamp - self.prev_timestamp[device_id])

        self.prev_timestamp[device_id] = time_stamp

        delta = delta + TIME_STAMP_RANGE if delta < 0 else delta

        data[0] = delta * TIME_SCALE

        return {"device_id": device_id,
                "delta": data[0],
                "gyro": self.gyro_remap(data[1:4]),
                "acc": data[4:7],
                "mag": data[7:10]}

    def __call__(self, from_uart=False, path='', realtime=True):
        self.in_loop = True
        self.is_running = True

        if from_uart:
            self.serial = serial.Serial(self.serial_port,
                                        self.baude_rate, timeout=0)

            self.data_buffer = ''

            self.prev_timestamp = [None, None]

            while self.in_loop:
                for data in self.get_data():
                    yield data
                sleep(0.05)
            self.serial.close()
            self.is_running = False
        else:
            with open(path, 'r') as f:
                for line in f:
                    if not self.in_loop:
                        raise GeneratorExit

                    data = map(float, line.split())
                    if realtime:
                        sleep(data[0])
                    yield {'delta': data[0],
                           'acc': data[1:4],
                           'mag': data[4:7],
                           'gyro': data[7:10]}

    def stop(self):
        self.in_loop = False

    def set_feedback(self, device_id, r, g, b, blink_on, blink_off, vibro):
        self.serial.write('set %d %d,%d,%d,%d,%d,%d\r' %
                          (device_id, r, g, b, blink_on, blink_off, vibro))
