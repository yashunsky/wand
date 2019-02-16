#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
from collections import namedtuple
from enum import Enum

import tkinter as tk
from tkinter.font import Font

from spells import ALL_SPELLS


# class House(Enum):
#     GRYFFINDOR = ('#c9000f', '#f69e34')
#     HUFFLEPUFF = ('#fef24f', '#000000')
#     RAVENCLAW = ('#0e0a9a', '#804733')
#     SLYTHERIN = ('#00410e', '#dcdcdc')

class House(Enum):
    GRYFFINDOR = '#ff0000'
    HUFFLEPUFF = '#fff300'
    RAVENCLAW = '#0006f2'
    SLYTHERIN = '#26ad06'


Duellist = namedtuple('Duellist', ['name', 'house'])


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
        self.sequence.set('Hs')

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

    def set_sequence(self, value):
        self.sequence.set(value)

    def set_timeout(self, value):
        self.timeout.set_value(value)

    def set_spells(self, spells):
        self.spells.set_text('\n'.join(spells))


class Ring(object):
    def __init__(self, duellists):
        super(Ring, self).__init__()

        window = tk.Tk()
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

        self.duellists = {device_id: DuellistFrame(window, config)
                          for device_id, config in configs.items()}

        self.duellists[0].pack(side='left', fill='y', expand=True)
        self.duellists[1].pack(side='right', fill='y', expand=True)

        window.configure(bg=basic_config['bg'])
        window.title('Дуэльный клуб')

        window.bind("<Key>", self.on_key)

        self.casted = []

    def make_config(self, basic_config, duellist):
        result = copy(basic_config)
        result['name'] = duellist.name
        result['self_color'] = duellist.house.value
        return result

    def on_key(self, event):
        self.casted.append(list(ALL_SPELLS.values())[len(self.casted)].name)
        self.duellists[0].set_spells(self.casted)

        self.duellists[0].set_sequence(event.char)

        try:
            v = int(event.char) * 2
            self.duellists[0].set_timeout(v)
        except:
            pass

if __name__ == '__main__':
    Ring([Duellist('Молли', House.GRYFFINDOR),
          Duellist('Беллатриса', House.SLYTHERIN)])

    tk.mainloop()
