#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
from threading import Thread
from time import sleep
import tkinter as tk
import tkinter.font as font

from .duellist_frame import DuellistFrame

KEYS = {
    'a': [0, 'Z'],
    'w': [0, 'Au'],
    'e': [0, 'Hu'],
    'r': [0, 'Du'],
    's': [0, 'As'],
    'd': [0, 'Hs'],
    'f': [0, 'Ds'],
    'x': [0, 'Au'],
    'c': [0, 'Hu'],
    'v': [0, 'Du'],
    'g': [0, 'N'],
    'q': [0, 'release'],

    'h': [1, 'Z'],
    'u': [1, 'Au'],
    'i': [1, 'Hu'],
    'o': [1, 'Du'],
    'j': [1, 'As'],
    'k': [1, 'Hs'],
    'l': [1, 'Ds'],
    'n': [1, 'Au'],
    'm': [1, 'Hu'],
    ',': [1, 'Du'],
    ';': [1, 'N'],
    'y': [1, 'release'],

    ' ': [None, 'random'],
}


class Ring(object):
    def __init__(self, duellists, pipe_in, pipe_out,
                 family=None, play_audio=False):
        super(Ring, self).__init__()

        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

        self.window = tk.Tk()

        self.play_audio = play_audio

        if family in font.families():
            fonts = {
                'name': font.Font(family=family, size=100),
                'sequence': font.Font(family=family, size=50),
                'to_parry': font.Font(family=family, size=50)
            }
        else:
            fonts = {
                'name': font.Font(size=100),
                'sequence': font.Font(size=50),
                'to_parry': font.Font(size=50)
            }

        basic_config = {
            'bg': '#ebcd89',
            'fg': '#64330c',
            'fonts': fonts,
            'max_timeout': 20
        }

        configs = {device_id: self.make_config(basic_config, duellist)
                   for device_id, duellist in enumerate(duellists)}

        configs[0]['adversery_color'] = configs[1]['self_color']
        configs[1]['adversery_color'] = configs[0]['self_color']

        if play_audio:
            from audio.player import Player
            self.player = Player()
            self.speach = Thread(target=self.speach_thread)
            self.speach.start()
        else:
            self.player = None

        self.duellists = {device_id: DuellistFrame(self.window, config,
                                                   device_id,
                                                   self.player)
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
        result['sex'] = duellist.value.sex
        return result

    def on_closing(self):
        self.in_loop = False
        self.pipe_out.send({'action': 'exit'})
        if self.play_audio:
            self.player.stop()
        sleep(0.1)
        self.window.destroy()

    def refresh_thread(self):
        while self.in_loop:
            if self.pipe_in.poll():
                message = self.pipe_in.recv()
                duellist = self.duellists[message['device_id']]
                if 'popup_type' in message:
                    duellist.set_popup(message)
                else:
                    duellist.set_sequence(message['sequence'])
                    duellist.set_timeout(message['timeout'])
                    duellist.set_spells(message['spells'])

            self.duellists[0].check_popup()
            self.duellists[1].check_popup()
            sleep(0.05)

    def speach_thread(self):
        self.player.play()

    def on_key(self, event):
        position = KEYS.get(event.char)
        if position is not None:
            device_id, code = position
            self.pipe_out.send({'action': 'position',
                                'device_id': device_id,
                                'position': code})
