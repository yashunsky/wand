#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from time import time
import tkinter as tk

from stick_control.position import decode_sequence

from .capital_text import CapitalText
from .progress_bar import ProgressBar
from .sequence import Sequence


POPUP_TIMEOUT = 4


class DuellistFrame(tk.Frame):
    def __init__(self, parent, config, sprites, device_id, player):
        super(DuellistFrame, self).__init__(parent, bg=config['bg'])
        self.side = 'right' if device_id else 'left'
        self.player = player
        self.sex = config['sex']

        self.sequence = []

        self.popup = tk.StringVar()
        self.popup.set('')

        name = CapitalText(self, config['bg'],
                           config['fg'],
                           config['fonts']['name'], config['self_color'])

        name.set_text(config['name'])
        name.pack(side='top', expand=False)

        self.sequence = Sequence(self, sprites, self.side, config['bg'])
        self.sequence.pack(side='top', expand=False)

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
            self.sequence.set(decode_sequence(value))
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
            args = (self.get_ending(), data['spell'].accusative)
            popup = 'Отбил%s %s' % args
        elif data['popup_type'] == 'defence_failed':
            prefix = 'Не отбил' if data['spell'].shields else 'Словил'
            args = (prefix, self.get_ending(), data['spell'].accusative)
            popup = '%s%s %s' % args
            self.sequence.remove_hint()
            self.enqueue_effect(data['spell'])
        elif data['popup_type'] == 'rule_of_3_failed':
            args = (self.get_ending(), data['spell'].accusative)
            popup = 'Нарушил%s правило трёх\nскастовав %s' % args
        elif data['popup_type'] == 'parry_needed':
            if data['spell'].shields:
                popup = 'Надо отбить %s' % data['spell'].accusative
                shield_sequence = decode_sequence(data['spell'].shields[0].key)
                self.sequence.set_hint(shield_sequence)
            self.enqueue_attack(data['spell'])

        if popup is not None:
            self.set_popup_text(popup)

    def enqueue_attack(self, spell):
        self.enqueue_audio(spell.audio_key)

    def enqueue_effect(self, spell):
        self.enqueue_audio('%s_effect' % spell.audio_key)

    def enqueue_audio(self, audio_key):
        if None not in (self.player, audio_key):
            self.player.enqueue((self.side, audio_key))

    def set_popup_text(self, popup):
        if popup != self.prev_popup:
            self.popup.set(popup)
            self.popup_time = time()
            self.prev_popup = popup

    def check_popup(self):
        if time() > self.popup_time + POPUP_TIMEOUT:
            self.set_popup_text('')
