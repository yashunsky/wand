#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
from time import sleep
import tkinter as tk
from tkinter.font import Font
from threading import Thread

from mages import Mage

KEYS = {
    'a': [0, 'Z'],
    's': [0, 'Au'],
    'd': [0, 'Hu'],
    'f': [0, 'Du'],
    'g': [0, 'N']
}


class DumpPipe(object):
    def __init__(self):
        super(DumpPipe, self).__init__()

    def send(self, value):
        pass

    def poll(self):
        return True

    def recv(self):
        return None


class CapitalText(tk.Text):
    def __init__(self, parent, bg, fg, font, capital_color):
        super(CapitalText, self).__init__(parent, bd=0, pady=0, padx=0,
                                          highlightthickness=0)
        self.tag_config('start', foreground=capital_color)
        self.configure(bg=bg, fg=fg,
                       width=1, height=1,
                       font=font, state=tk.DISABLED)

    def set_text(self, text):
        lines = text.split('\n')
        self.configure(state=tk.NORMAL,
                       width=max(map(lambda x: len(x), lines)),
                       height=len(lines))
        self.delete('1.0', tk.END)
        self.insert(tk.END, text)

        for l in range(len(lines)):
            line = l + 1
            self.tag_add('start', '%d.0' % line, '%d.1' % line)

        self.configure(state=tk.DISABLED)


class ProgressBar(tk.Text):
    def __init__(self, parent, bg, fg, font, color, max_value):
        super(ProgressBar, self).__init__(parent, bd=0, pady=0, padx=0,
                                          highlightthickness=0)

        self.tag_config('colored', foreground=color)
        self.insert(tk.END, '•' * max_value)
        self.configure(bg=bg, fg=fg,
                       width=max_value - 4, height=1,  # bad hack :(
                       font=font, state=tk.DISABLED)

    def set_value(self, value):
        self.configure(state=tk.NORMAL)
        self.tag_remove('colored', '1.0', tk.END)
        self.tag_add('colored', '1.0', '1.%d' % value)
        self.configure(state=tk.DISABLED)


class DuellistFrame(tk.Frame):
    def __init__(self, parent, config):
        super(DuellistFrame, self).__init__(parent, bg=config['bg'])

        self.sequence = tk.StringVar()
        self.sequence.set('')

        name = CapitalText(self, config['bg'],
                           config['fg'],
                           config['fonts']['name'], config['self_color'])

        name.set_text(config['name'])
        name.pack(side='top', expand=False)

        tk.Label(self, textvariable=self.sequence,
                 bg=config['bg'],
                 fg=config['fg'],
                 font=config['fonts']['sequence']).pack(side='top', fill='x',
                                                        expand=False)

        self.timeout = ProgressBar(self, config['bg'], config['fg'],
                                   config['fonts']['sequence'],
                                   config['self_color'],
                                   config['max_timeout'])
        self.timeout.pack(side='top', expand=False)

        self.spells = CapitalText(self, config['bg'], config['fg'],
                                  config['fonts']['to_parry'],
                                  config['adversery_color'])
        self.spells.pack(side='top', expand=False)

        self.prev_sequence = None
        self.prev_timeout = None
        self.prev_spells = None

    def set_sequence(self, value):
        if value != self.prev_sequence:
            self.sequence.set(value)
        self.prev_sequence = value

    def set_timeout(self, value):
        if value != self.prev_timeout:
            self.timeout.set_value(value)
        self.prev_timeout = value

    def set_spells(self, spells):
        if spells != self.prev_spells:
            self.spells.set_text('\n'.join(spells))
        self.prev_spells = spells


class Ring(object):
    def __init__(self, duellists, pipe_in=DumpPipe(), pipe_out=DumpPipe()):
        super(Ring, self).__init__()

        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

        self.window = tk.Tk()
        family = 'Agatha-Modern'

        basic_config = {
            'bg': '#fcf3cb',
            'fg': '#64330c',
            'fonts': {
                'name': Font(family=family, size=100),
                'sequence': Font(family=family, size=50),
                'to_parry': Font(family=family, size=50)
            },
            'max_timeout': 20
        }

        configs = {device_id: self.make_config(basic_config, duellist)
                   for device_id, duellist in enumerate(duellists)}

        configs[0]['adversery_color'] = configs[1]['self_color']
        configs[1]['adversery_color'] = configs[0]['self_color']

        self.duellists = {device_id: DuellistFrame(self.window, config)
                          for device_id, config in configs.items()}

        self.duellists[0].pack(side='left', fill='y', expand=True)
        self.duellists[1].pack(side='right', fill='y', expand=True)

        self.window.configure(bg=basic_config['bg'])
        self.window.title('Дуэльный клуб')

        self.window.bind("<Key>", self.on_key)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.in_loop = True
        self.refresh = Thread(target=self.refresh_thread)
        self.refresh.start()

    def make_config(self, basic_config, duellist):
        result = copy(basic_config)
        result['name'] = duellist.value.name
        result['self_color'] = duellist.value.house.value
        return result

    def on_closing(self):
        self.in_loop = False
        self.pipe_out.send({'action': 'exit'})
        sleep(0.1)
        self.window.destroy()

    def refresh_thread(self):
        while self.in_loop:
            if self.pipe_in.poll():
                message = self.pipe_in.recv()
                duellist = self.duellists[message['device_id']]
                duellist.set_sequence(message['sequence'])
                duellist.set_timeout(message['timeout'])
                duellist.set_spells(message['spells'])
            sleep(0.05)

    def on_key(self, event):
        position = KEYS.get(event.char)
        if position is not None:
            device_id, code = position
            self.pipe_out.send({'action': 'position',
                                'device_id': device_id,
                                'position': code})


if __name__ == '__main__':
    Ring([Mage.MOLLY, Mage.BELLATRIX])

    tk.mainloop()
