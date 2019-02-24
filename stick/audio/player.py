#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
from time import sleep
import os
import pyaudio
import wave

CHUNK = 1024
FILE_TEMPLATE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'sounds',
    '%s.wav')


class Side(object):
    def __init__(self, open_file):
        super(Side, self).__init__()
        self.sequence = []
        self.wf = None
        self.data = None
        self.open_file = open_file

    def enqueue(self, key):
        self.sequence.append(key)

    def get_data(self):
        if self.sequence and self.wf is None:
            self.wf = self.open_file(self.sequence.pop(0))

        if self.wf is not None:
            self.data = self.wf.readframes(CHUNK)
            if len(self.data) == 0:
                self.data = None
                self.wf = None

        return copy(self.data)


class Player(object):
    def __init__(self, stop_when_done=False):
        super(Player, self).__init__()
        self.stream = None
        self.p = None
        self.format = None
        self.left_side = Side(self.open_file)
        self.right_side = Side(self.open_file)
        self.in_loop = True
        self.stop_when_done = stop_when_done

    def stream_from_wav(self, wf):
        self.format = self.p.get_format_from_width(wf.getsampwidth())
        return self.p.open(format=self.format,
                           channels=wf.getnchannels(),
                           rate=wf.getframerate(),
                           output=True)

    def enqueue(self, element):
        side, key = element
        (self.left_side if side == 'left' else self.right_side).enqueue(key)

    def mix(self, left, right):
        if left is None:
            left = [0] * len(right)
        if right is None:
            right = [0] * len(left)

        audio_bytes = self.format * 2 // 8

        return bytes([l if not (id // audio_bytes) % 2 else r
                      for id, (l, r) in enumerate(zip(left, right))])

    def open_file(self, filename):
        wf = wave.open(FILE_TEMPLATE % filename, 'rb')
        if self.stream is None:
            self.stream = self.stream_from_wav(wf)
        return wf

    def play(self):
        try:
            self.p = pyaudio.PyAudio()
            while self.in_loop:
                left = self.left_side.get_data()
                right = self.right_side.get_data()

                if left is not None or right is not None:
                    self.stream.write(self.mix(left, right))

                else:
                    if self.stop_when_done:
                        self.in_loop = False
                    else:
                        sleep(0.05)
        finally:
            self.terminate()

    def stop(self):
        self.in_loop = False

    def terminate(self):
        if self.p is not None:
            self.p.terminate()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()


if __name__ == '__main__':
    player = Player(stop_when_done=True)
    player.enqueue(('left', 'incendio'))
    player.enqueue(('right', 'deluvium_effect'))
    player.play()
