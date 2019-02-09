#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import serial

from time import sleep

SERIAL_PORT = '/dev/tty.usbmodem1411'

BAUDE_RATE = 115200
BUFFER_DELIMITER = '\r'

TIME_SCALE = 0.0001  # s/digit
MAX_DELTA = 10
TIME_STAMP_RANGE = 2 ** 32


class UartReader(object):
    def __init__(self, serial_port=SERIAL_PORT, dual=False):
        super(UartReader, self).__init__()
        self.serial_port = serial_port
        self.dual = dual

        self.in_loop = False
        self.is_running = False

        self.prev_timestamp = [None, None]

        self.first_line = True

    def get_data(self):
        self.data_buffer += self.serial.read(self.serial.inWaiting()).decode()

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
                result = self.parse_line(line)
                if result is not None:
                    yield result

    def parse_line(self, line):
        try:
            data = [float(value) for value in line.split(';')]
        except ValueError:
            return None

        device_id = 0
        time_stamp = data[0]
        button = data[1] > 0

        delta = (0 if self.prev_timestamp[device_id] is None
                 else time_stamp - self.prev_timestamp[device_id])

        self.prev_timestamp[device_id] = time_stamp

        delta = delta + TIME_STAMP_RANGE if delta < 0 else delta

        delta *= TIME_SCALE

        if delta > MAX_DELTA:
            delta = 0

        return {'device_id': device_id,
                'button': button,
                'delta': delta,
                'gyro': data[2:5],
                'acc': data[5:8]}

    def __call__(self, from_uart=True, path='', realtime=True):
        self.in_loop = True
        self.is_running = True

        if from_uart:
            self.data_buffer = ''

            self.prev_timestamp = [None, None]

            try:
                self.serial = serial.Serial(self.serial_port, timeout=0)
                while self.in_loop:
                    for data in self.get_data():
                        yield data
                    sleep(0.05)
            finally:
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
