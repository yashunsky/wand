#!/usr/bin/env python
# -*- coding: utf8 -*-

import serial

from time import sleep

SERIAL_PORT = '/dev/tty.usbmodem1411'

BAUDE_RATE = 115200
BUFFER_DELIMITER = '\r'

TIME_SCALE = 0.001  # s/digit
ACC_SCALE = 1
MAG_SCALE = 1
GYRO_SCALE = 1  # 1.0 / 300  # ????

TIME_STAMP_RANGE = 2 ** 32


class InputGenerator(object):
    def __init__(self, serial_port=SERIAL_PORT):
        super(InputGenerator, self).__init__()
        self.serial_port = serial_port

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
            yield self.parse_line(line)

    def parse_line(self, line):
        data = [float(value) for value in line.replace(";", "").split()]
        time_stamp = data[0]

        delta = (0 if self.prev_timestamp is None
                 else time_stamp - self.prev_timestamp)

        self.prev_timestamp = time_stamp

        delta = delta + TIME_STAMP_RANGE if delta < 0 else delta

        data[0] = delta * TIME_SCALE

        return {"delta": data[0],
                "acc": [x * ACC_SCALE for x in data[1:4]],
                "mag": [x * MAG_SCALE for x in data[4:7]],
                "gyro": [x * GYRO_SCALE for x in data[7:10]]}

    def __call__(self, from_uart=False, path='', realtime=True):
        self.in_loop = True

        if from_uart:
            self.serial = serial.Serial(self.serial_port,
                                        BAUDE_RATE, timeout=0)

            self.data_buffer = ''

            self.prev_timestamp = None

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
                        yield data
                sleep(0.05)
            self.serial.close()
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
