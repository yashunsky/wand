#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
from time import sleep
from uuid import uuid4

import os
import tkinter as tk

from stick_control.uart_reader import UartReader


class Display(object):
    def __init__(self, pipe_out):
        super(Display, self).__init__()

        self.pipe_out = pipe_out

        self.window = tk.Tk()
        self.window.bind("<Key>", self.on_key)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.title('cast recorder')
        self.window.geometry('400x100')

        self.cast_value = tk.StringVar()
        self.cast_lable = tk.Label(self.window,
                                   textvariable=self.cast_value,
                                   font=('Arial', 100))
        self.cast_lable.pack()

        self.cast_value.set('')

    def on_key(self, event):
        self.cast_value.set(event.char)
        self.pipe_out.send({'cast': event.char})

    def on_closing(self):
        self.pipe_out.send({'action': 'stop'})
        sleep(0.1)
        self.window.destroy()


def start_gui(pipe_in):
    Display(pipe_in)
    tk.mainloop()


def start_main_thread(pipe_in):
    cast_letter = None
    cast_file = None
    cast = []
    raw_stream = UartReader()

    def print_line(cast_line):
        args = tuple([cast_line[0]] + cast_line[1] + cast_line[2])
        return '%.2f a %i %i %i g %i %i %i\n' % args

    for raw_data in raw_stream():
        if pipe_in.poll():
            message = pipe_in.recv()
            if message.get('action') == 'stop':
                raw_stream.stop()
            elif 'cast' in message:
                cast_letter = message['cast']

        if raw_data['button']:
            if cast_file is None:
                cast_file = uuid4().hex
                cast = []
            cast.append([raw_data[key] for key in ['delta', 'acc', 'gyro']])

        if not raw_data['button'] and cast_file is not None:
            if cast_letter is not None:
                folder_path = os.path.join('raw', cast_letter)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                with open(os.path.join(folder_path, cast_file), 'w') as f:
                    f.write(''.join([print_line(line) for line in cast]))
            cast_file = None


if __name__ == '__main__':
    from_gui_parent, from_gui_child = Pipe(duplex=False)

    p = Process(target=start_main_thread, args=(from_gui_parent,))
    p.start()
    start_gui(from_gui_child)
    p.join()
