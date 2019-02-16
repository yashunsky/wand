#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from setup import SHIELD_TIMEOUT, ACTION_TIMEOUT
from spells import AVADA


class Duellist(object):
    def __init__(self, stick_id,
                 on_defence_succeded=lambda a, d: None,
                 on_defence_failed=lambda s: None,
                 on_rule_of_3_failed=lambda s: None,
                 on_death=lambda s: None):
        super(Duellist, self).__init__()
        self.stick_id = stick_id
        self.sequence = ''
        self.vibro = 0
        self.timeout = SHIELD_TIMEOUT
        self.catched_spells = []
        self.adversary = None
        self.on_defence_succeded = on_defence_succeded
        self.on_defence_failed = on_defence_failed
        self.on_rule_of_3_failed = on_rule_of_3_failed
        self.on_death = on_death
        self.attacks_buffer = []

        self.action_timeout = 0

        self.is_defending = False

    def set_adversary(self, adversary):
        self.adversary = adversary

    def catch_spell(self, spell):
        if spell == AVADA:
            self.on_death(spell)
        else:
            self.catched_spells.append(spell)

    def remove_top_spell(self):
        self.catched_spells = self.catched_spells[1:]
        self.timeout = SHIELD_TIMEOUT

    def cast_spell(self, spell):
        if self.catched_spells:
            top_spell = self.catched_spells[0]
            if spell in top_spell.shields:
                self.on_defence_succeded(top_spell, spell)
                self.remove_top_spell()
                return

        if spell.is_attack and self.adversary is not None:
            self.adversary.catch_spell(spell)
            if spell.breaks_rull_of_3:
                if (spell in self.attacks_buffer[-2:] and
                   not spell.ignore_rule_of_3):
                    self.on_rule_of_3_failed(spell)
                self.attacks_buffer = (self.attacks_buffer + [spell])[-3:]

    def set_state(self, delta, sequence='', vibro=0,
                  spell=None, action_timeout=0):
        self.sequence = sequence
        self.vibro = vibro
        self.action_timeout = action_timeout
        if spell is not None:
            self.cast_spell(spell)

        if self.catched_spells:
            self.timeout -= delta
            expexted_prefixes = self.catched_spells[0].shields_prefixes
            self.is_defending = self.sequence in expexted_prefixes
            if not self.is_defending and self.timeout < 0:
                self.on_defence_failed(self.catched_spells[0])
                self.remove_top_spell()

    def for_gui(self):
        if self.catched_spells and not self.is_defending:
            timeout = int((float(max(self.timeout, 0)) * 20 / SHIELD_TIMEOUT))
        elif self.vibro > 0:
            timeout = int((float(max(self.action_timeout, 0)) * 20 / ACTION_TIMEOUT))
        else:
            timeout = 0

        return {
            'device_id': self.stick_id,
            'sequence': self.sequence,
            'spells': [spell.name for spell in self.catched_spells],
            'timeout': timeout
        }
