#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import pyaudio
import wave
from time import sleep


CHUNK = 1024
FILE_TEMPLATE = 'sounds/%s.wav'


class Player(object):
    def __init__(self, stop_when_done=False):
        super(Player, self).__init__()
        self.stream = None
        self.p = None
        self.sequence = []
        self.in_loop = True
        self.stop_when_done = stop_when_done

    def stream_from_wav(self, wf):
        format = self.p.get_format_from_width(wf.getsampwidth())
        return self.p.open(format=format,
                           channels=wf.getnchannels(),
                           rate=wf.getframerate(),
                           output=True)

    def enqueue(self, element):
        self.sequence.append(element)

    def play(self):
        try:
            self.p = pyaudio.PyAudio()
            while self.in_loop:
                if self.sequence:
                    side, filename = self.sequence.pop(0)

                    wf = wave.open(FILE_TEMPLATE % filename, 'rb')

                    if self.stream is None:
                        stream = self.stream_from_wav(wf)

                    data = wf.readframes(CHUNK)

                    while len(data) > 0 and self.in_loop:
                        stream.write(data)
                        data = wf.readframes(CHUNK)

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
    # play(DumpPipe(), [('left', 'incendio'), ('right', 'deluvium_effect')])
    player = Player(stop_when_done=True)
    player.enqueue(('left', 'incendio'))
    player.enqueue(('right', 'deluvium_effect'))
    player.play()
