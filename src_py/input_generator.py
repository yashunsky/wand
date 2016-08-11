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
    def __init__(self, serial_port=SERIAL_PORT, dual=False):
        super(InputGenerator, self).__init__()
        self.serial_port = serial_port
        self.dual = dual

        self.in_loop = False
        self.is_running = False

        self.prev_timestamp = [None, None]

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
            if line:
                print line
                yield self.parse_line(line)

    def parse_line(self, line):
        data = [float(value) for value in line.replace(";", "").split()]

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
                "gyro": data[1:4],
                "acc": data[4:7],
                "mag": data[7:10]}

    def __call__(self, from_uart=False, path='', realtime=True):
        self.in_loop = True
        self.is_running = True

        if from_uart:
            self.serial = serial.Serial(self.serial_port,
                                        BAUDE_RATE, timeout=0)

            self.data_buffer = ''

            self.prev_timestamp = [None, None]

            min_max_mag = [float('Inf')] * 3 + [-float('Inf')] * 3

            while self.in_loop:
                for data in self.get_data():
                    mag = data['mag']
                    if mag:
                        for i in xrange(3):
                            if mag[i] < min_max_mag[i]:
                                min_max_mag[i] = mag[i]
                            if mag[i] > min_max_mag[i + 3]:
                                min_max_mag[i + 3] = mag[i]
                        # print min_max_mag
                        if not self.dual:
                            del data['device_id']
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

    def set_feedback(self, feedback):
        self.serial.write('set 0 %d,%d,%d,%d\r' % feedback)
