#! /usr/bin/python
# -*- coding: utf8 -*-

from c_wrap import set_lightsaber_data
from input_generator import InputGenerator

PORT = '/dev/tty.usbserial-A9IX9R77'

PRESCALER = 10


def main():

    tick = 0

    input_generator = InputGenerator(serial_port=PORT, baude_rate=256000)

    for input_data in input_generator(True, '', True):
        tick += 1
        try:
            hum = set_lightsaber_data(input_data['delta'],
                                      input_data['acc'],
                                      input_data['gyro'],
                                      input_data['mag'])
            if tick % PRESCALER == 0:
                print '-' * hum
        except KeyboardInterrupt:
            input_generator.in_loop = False

if __name__ == '__main__':
    main()
