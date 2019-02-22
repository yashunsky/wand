#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
from random import choice
import subprocess
from time import time, sleep
import tkinter as tk
import tkinter.font as font
from threading import Thread

from mages import Mage

POPUP_TIMEOUT = 4

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
                       width=max(map(lambda x: len(x), lines)) + 1,
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
    def __init__(self, parent, config, side, speach_queue):
        super(DuellistFrame, self).__init__(parent, bg=config['bg'])
        self.side = side
        self.speach_queue = speach_queue
        self.sex = config['sex']

        self.sequence = tk.StringVar()
        self.sequence.set('')

        self.popup = tk.StringVar()
        self.popup.set('')

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

        tk.Label(self, textvariable=self.popup,
                 bg=config['bg'],
                 fg=config['fg'],
                 font=config['fonts']['sequence']).pack(side='bottom',
                                                        fill='x',
                                                        expand=False)

        self.prev_sequence = None
        self.prev_timeout = None
        self.prev_spells = None
        self.prev_popup = None

        self.popup_time = 0

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

    def get_ending(self):
        return '' if self.sex == 'M' else 'а'

    def set_popup(self, data):
        popup = None
        if data['popup_type'] == 'defence_succeded':
            args = (self.get_ending(),
                    data['spells'][0].accusative,
                    data['spells'][1].accusative)
            popup = 'Отбил%s %s,\nскастовав %s' % args
        elif data['popup_type'] == 'defence_failed':
            prefix = 'Не отбил' if data['spells'].shields else 'Словил'
            args = (prefix, self.get_ending(), data['spells'].accusative)
            popup = '%s%s %s' % args
        elif data['popup_type'] == 'rule_of_3_failed':
            args = (self.get_ending(), data['spells'].accusative)
            popup = 'Нарушил%s правило трёх\nскастовав %s' % args
        elif data['popup_type'] == 'death':
            popup = 'Убит%s' % self.get_ending()
        elif data['popup_type'] == 'parry_needed':
            if data['spells'].shields:
                popup = 'Надо отбить %s' % data['spells'].accusative
            self.say_something_on_attack(data['spells'])

        if popup is not None:
            self.set_popup_text(popup)
            # self.speach_queue.append((self.sex, popup))

    def say_something_on_attack(self, spell):
            if spell.shields:
                to_say = choice(['отбей %s' % spell.accusative,
                                 'ой, %s' % spell.name,
                                 'кастуй %s' % spell.shields[0]])
            else:
                to_say = choice(['безнадёжно',
                                 'ничто не поможет',
                                 'непростиловка'])

            self.speach_queue.append((self.sex, to_say))

    def set_popup_text(self, popup):
        if popup != self.prev_popup:
            self.popup.set(popup)
            self.popup_time = time()
            self.prev_popup = popup

    def check_popup(self):
        if time() > self.popup_time + POPUP_TIMEOUT:
            self.set_popup_text('')


class Ring(object):
    def __init__(self, duellists, pipe_in, pipe_out,
                 family=None, play_audio=False):
        super(Ring, self).__init__()

        self.pipe_in = pipe_in
        self.pipe_out = pipe_out

        self.window = tk.Tk()

        self.play_audio = play_audio
        self.speach_queue = []

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

        self.duellists = {device_id: DuellistFrame(self.window, config,
                                                   device_id,
                                                   self.speach_queue)
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

        self.speach = Thread(target=self.speach_thread)
        self.speach.start()

    def make_config(self, basic_config, duellist):
        result = copy(basic_config)
        result['name'] = duellist.value.name
        result['self_color'] = duellist.value.house.value
        result['sex'] = duellist.value.sex
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
        if self.play_audio:
            while self.in_loop:
                if self.speach_queue:
                    sex, message = self.speach_queue.pop(0)
                    subprocess.run(['say', '-v',
                                    'Yuri' if sex == 'M' else 'Milena',
                                    message])
                sleep(0.05)

    def on_key(self, event):
        position = KEYS.get(event.char)
        if position is not None:
            device_id, code = position
            self.pipe_out.send({'action': 'position',
                                'device_id': device_id,
                                'position': code})


if __name__ == '__main__':
    Ring([Mage.GODRIC, Mage.SALAZAR], DumpPipe(), DumpPipe())
    import tkinter.font as f
    print(f.families())
    tk.mainloop()
