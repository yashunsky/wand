#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk

from time import sleep
from threading import Thread


DISPLAY_STATES = {'calibration': u'идет калибровка',
                  'idle': u'ждём жеста',
                  'splitting': u'жест'}


class DumpPipe(object):
    """docstring for DumpPipe"""
    def __init__(self):
        super(DumpPipe, self).__init__()

    def send(self, value):
        pass

    def poll(self):
        pass


class Widget(object):
    def __init__(self, pipe_in, pipe_out):
        super(Widget, self).__init__()

        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window.resizable(width=False, height=False)

        self.label = tk.StringVar()

        self.label.set(u'Ready')

        tk.Label(self.window, textvariable=self.label,
                 font=("Helvetica", 64),
                 width=30, height=5).pack()

        self.button = tk.Button(self.window, text=u'следующий жест',
                                command=self.callback)
        self.button.pack()
        self.in_loop = True
        self.refresh = Thread(target=self.refresh_thread)
        self.refresh.start()

    def callback(self):
        self.pipe_out.send('next')

    def on_closing(self):
        self.in_loop = False
        self.pipe_out.send('exit')
        sleep(0.1)
        self.window.destroy()

    def set_state(self, new_display_state, subtitle=''):
        self.display_state = new_display_state

        if self.display_state in DISPLAY_STATES:
            display_state = DISPLAY_STATES[self.display_state]
            self.label.set(display_state + '\n' + subtitle)
        else:
            self.label.set(self.display_state)

    def refresh_thread(self):
        while self.in_loop:
            if self.pipe_in.poll():
                display_state, subtitle = self.pipe_in.recv()
                self.set_state(display_state, subtitle)
            sleep(0.01)


if __name__ == '__main__':

    widget = Widget(DumpPipe(), DumpPipe())

    tk.mainloop()
