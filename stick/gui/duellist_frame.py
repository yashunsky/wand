#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import choice
from time import time
import tkinter as tk

from knowledge.spells import ALL_SPELLS
from stick_control.position import decode_sequence

from .capital_text import CapitalText
from .progress_bar import ProgressBar
from .sequence import Sequence


POPUP_TIMEOUT = 4
POPUP_WIDTH = 20


class DuellistFrame(tk.Frame):
    def __init__(self, parent, config, sprites, device_id, player, pipe):
        super(DuellistFrame, self).__init__(parent, bg=config['bg'])
        self.device_id = device_id
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
        name.bind("<Button-1>", self.switch_auto)

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
                 width=POPUP_WIDTH,
                 font=config['fonts']['sequence']).pack(side='bottom',
                                                        fill='x',
                                                        expand=False)

        self.prev_sequence = None
        self.prev_timeout = None
        self.prev_spells = None
        self.prev_popup = None

        self.attacks_buffer = []

        self.popup_time = 0

        self.sheild_hint = None

        self.auto = False

        self.pipe = pipe

    def set_auto(self, value):
        self.auto = value
        self.pipe.send({'device_id': self.device_id,
                        'action': 'auto',
                        'value': self.auto})

    def switch_auto(self, *args):
        self.set_auto(not self.auto)

    def set_sequence(self, value):
        if value != self.prev_sequence:
            self.sequence.set(decode_sequence(value))
            self.prev_sequence = value
            self.set_attack_hint_if_needed()

    def set_timeout(self, value):
        if value != self.prev_timeout:
            self.timeout.set_value(value)
            self.prev_timeout = value

    def set_spells(self, spells):
        if spells != self.prev_spells:
            self.spells.set_text('\n'.join(spells))
            self.prev_spells = spells
            self.set_attack_hint_if_needed()

    def set_attacks_buffer(self, value):
        self.attacks_buffer = value

    def done_recently(self, spell):
        return spell.key in self.attacks_buffer

    def get_ending(self):
        return '' if self.sex == 'M' else 'а'

    def set_popup(self, data):
        popup = None
        if data['popup_type'] == 'defence_succeded':
            args = (self.get_ending(), data['spell'])
            popup = 'Отбил%s %s' % args
        elif data['popup_type'] == 'defence_failed':
            prefix = 'Не отбил' if data['spell'].shields else 'Словил'
            args = (prefix, self.get_ending(), data['spell'])
            popup = '%s%s %s' % args
            self.enqueue_effect(data['spell'])
            self.set_auto(False)
        elif data['popup_type'] == 'rule_of_3_failed':
            args = (self.get_ending(), data['spell'])
            popup = 'Нарушил%s правило трёх,\nскастовав %s' % args
        elif data['popup_type'] == 'parry_needed':
            if data['spell'].shields:
                popup = 'Надо отбить %s' % data['spell']
                shield_sequence = decode_sequence(data['spell'].shields[0].key)
                self.sheild_hint = shield_sequence
                if self.prev_sequence == '':
                    self.sequence.set_hint(shield_sequence)
            self.enqueue_attack(data['spell'])

        if popup is not None:
            self.set_popup_text(popup)

    def set_suatble_hint(self):
        if self.auto:
            if self.sequence.is_hint_set():
                self.sequence.remove_hint()
        elif not self.sequence.is_hint_set() and self.prev_sequence == '':
            if self.prev_spells:
                self.sequence.set_hint(self.sheild_hint)
            else:
                self.set_attack_hint_if_needed()

    def set_attack_hint_if_needed(self):
        if self.prev_sequence != '' or self.prev_spells:
            return
        spell = choice([spell for spell in ALL_SPELLS.values()
                        if spell.shields and not self.done_recently(spell)])
        shield_sequence = decode_sequence(spell.key)
        self.sequence.set_hint(shield_sequence)

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

    def refresh(self):
        if time() > self.popup_time + POPUP_TIMEOUT:
            self.set_popup_text('')
        self.set_suatble_hint()
