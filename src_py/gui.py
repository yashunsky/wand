#!/usr/bin/python
# -*- coding: utf-8 -*-

import Tkinter as tk

from time import sleep, time
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
        return True

    def recv(self):
        return ({'active': True,
                 'color': '#FFEE00',
                 'blink': 1,
                 'vibro': 30}, '')

COLORS = [
    '#000000',
    '#FFFFFF',
    '#FF0000',
    '#FF8800',
    '#FFFF00',
    '#00FF00',
    '#0000FF',
    '#FF00FF'
]


def decode_vibro(vibro):
    if vibro == 0:
        return ''
    return u'б' + u'ж' * int((vibro / 100.0) * 5 + 1)


class Widget(object):
    def __init__(self, pipe_in, pipe_out):
        super(Widget, self).__init__()

        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window.resizable(width=False, height=False)

        self.label_str = tk.StringVar()

        self.label_str.set(u'Ready')

        self.label = tk.Label(self.window, textvariable=self.label_str,
                              font=("Helvetica", 64),
                              width=30, height=5)

        self.label.pack()

        self.button = tk.Button(self.window, text=u'следующий жест',
                                command=self.callback)
        self.button.pack()
        self.in_loop = True
        self.state = None
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

        if isinstance(self.display_state, dict):
            s = self.display_state
            if not s['active']:
                text = u'Идёт калибровка'
                bg = 'black'
                fg = 'white'
            else:
                if s['blink'] == 0:
                    bg = 'black'
                else:
                    blink = ((time() * 4) // (3 - s['blink'])) % 2
                    bg = COLORS[s['color']] if blink else 'black'
                fg = 'white' if bg == 'black' else 'black'

                text = decode_vibro(s['vibro'])
            self.label.configure(background=bg)
            self.label.configure(fg=fg)
            self.label_str.set(text)

        elif self.display_state in DISPLAY_STATES:
            display_state = DISPLAY_STATES[self.display_state]
            self.label.set(display_state + '\n' + subtitle)

    def refresh_thread(self):
        while self.in_loop:
            if self.pipe_in.poll():
                self.state = self.pipe_in.recv()
            if self.state is not None:
                self.set_state(*self.state)
            sleep(0.05)


if __name__ == '__main__':

    widget = Widget(DumpPipe(), DumpPipe())

    tk.mainloop()
