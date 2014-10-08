#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''Psedo Serial Port
This module should be included instead of 'serial'
'''

from time import time, sleep

DATA_PATH = '../data.raw'

RAW_DELIMITER = '\r\n'
BUFFER_DELIMITER = '\r\n'

class Serial(object):
    """A psedo serial port object, acting on demand,
    and passing data from *.raw file"""
    def __init__(self, *args):
        super(Serial, self).__init__()
        self.timer = None
        self.buffer = ''
        self.file_offset = 0
        self.previus_timestamp = None

    def update_data(self):
        now = time()
        if self.timer is None: # first call
            # self.timer is used to calc the time,
            # passed betwen calls
            self.timer = now

            # get timestamp from the *.raw file's first line
            with open(DATA_PATH, 'r') as f:
                for line in f:
                    self.previus_timestamp = float(line.split()[0])
                    break
            return
        else: # all others calls
            delay = now - self.timer

            # set passed_timestamp default value
            # it would be changed, if only a line from raw file
            # will be put in buffer
            passed_timestamp = self.previus_timestamp
            with open(DATA_PATH, 'r') as f:
                f.seek(self.file_offset)
                for line in f:
                    timestamp, buffer_line = line.split(' ', 1)
                    timestamp = float(timestamp)
                    if timestamp - self.previus_timestamp < delay:
                        # add line to buffer
                        buffer_line = buffer_line.replace(RAW_DELIMITER,
                                                          BUFFER_DELIMITER)
                        self.buffer += buffer_line

                        # move file pointer for next opening
                        self.file_offset += len(line)

                        # adjust file and object time counters
                        passed_timestamp = timestamp
                        self.timer = now
                    else:
                        break
            # self.previus_timestamp shoold keep const
            # during file's lines itteration,
            # now it can be changed 
            self.previus_timestamp = passed_timestamp


    def inWaiting(self):
        self.update_data()
        return len(self.buffer)

    def read(self, count):
        self.update_data()
        result, self.buffer = self.buffer[:count], self.buffer[count:]
        return result

if __name__ == '__main__':
    serial = Serial()

    print '>>>', serial.read(serial.inWaiting())
    quit()
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    sleep(0.6)
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    sleep(0.02)
    print '>>>', serial.read(serial.inWaiting())
