#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from setup import SHIELD_TIMEOUT


class Duellist(object):
    def __init__(self, stick_id,
                 on_defence_succeded=lambda a, d: None,
                 on_defence_failed=lambda s: None,
                 on_rule_of_3_failed=lambda s: None):
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
        self.attacks_buffer = []

    def set_adversary(self, adversary):
        self.adversary = adversary

    def catch_spell(self, spell):
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
            if spell in self.attacks_buffer[-2:]:
                self.on_rule_of_3_failed(spell)
            self.attacks_buffer = (self.attacks_buffer + [spell])[-3:]

    def set_state(self, delta, sequence='', vibro=0, spell=None):
        self.sequence = sequence
        self.vibro = vibro
        if spell is not None:
            self.cast_spell(spell)

        if self.catched_spells:
            self.timeout -= delta
            expexted_prefixes = self.catched_spells[0].shields_prefixes
            is_defending = self.sequence in expexted_prefixes
            if not is_defending and self.timeout < 0:
                self.on_defence_failed(self.catched_spells[0])
                self.remove_top_spell()
