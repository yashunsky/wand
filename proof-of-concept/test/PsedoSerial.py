#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''Psedo Serial Port
This module should be included instead of 'serial'
'''

from time import time, sleep
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data.raw')

RAW_DELIMITER = '\r\n'
BUFFER_DELIMITER = '\r\n'

class Serial(object):
    """A psedo serial port object, acting on demand,
    and passing data from *.raw file"""
    def __init__(self, port, baude_rate, timeout=0):
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
            # it can be moved to __init__ but any way
            # we can't return anything on first call
            # because self.timer needs to be set
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
    serial = Serial('serial', 115200, 0)

    print 'serial.read(serial.inWaiting()) call Serial.update() twice '
    print '1-2: setting up timers'
    print '>>>', serial.read(serial.inWaiting())
    print 'inWaiting returned 0, nothing read.'
    print '3-4: on call #2 files\' first line was put into the buffer'
    print '>>>', serial.read(serial.inWaiting())
    print 'now it was read'
    print '5-6: we\'re calling too often'
    print '>>>', serial.read(serial.inWaiting())
    print 'nothing happens. let\'s wait 0.6s'
    sleep(0.6)
    print '7-8:'
    print '>>>', serial.read(serial.inWaiting())
    print 'ta-dam: got 2 new lines'
    print '9-14:'
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    print '>>>', serial.read(serial.inWaiting())
    print 'anther too often calls with no result'
    print '15-16: 0.02sec pause is ok to get one new line'
    sleep(0.02)
    print '>>>', serial.read(serial.inWaiting())
    print 'and here it is'
