#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import copy
from random import choice, random

from knowledge.setup import SHIELD_TIMEOUT, ACTION_TIMEOUT, GUI_MAX_TIMEOUT
from knowledge.setup import AUTO_REACTION, AUTO_PAUSE
from knowledge.spells import ALL_SPELLS


class Duellist(object):
    def __init__(self, stick_id,
                 on_parry_needed=lambda s: None,
                 on_defence_succeded=lambda s: None,
                 on_defence_failed=lambda s: None,
                 on_rule_of_3_failed=lambda s: None,
                 on_auto=lambda p: None,
                 auto_base_timeout=None):
        super(Duellist, self).__init__()
        self.stick_id = stick_id
        self.sequence = ''
        self.doing_well = False
        self.timeout = 0
        self.catched_spells = []
        self.adversary = None
        self.on_parry_needed = on_parry_needed
        self.on_defence_succeded = on_defence_succeded
        self.on_defence_failed = on_defence_failed
        self.on_rule_of_3_failed = on_rule_of_3_failed
        self.attacks_buffer = []

        self.action_timeout = 0

        self.is_defending = False

        self.auto_base_timeout = auto_base_timeout
        self.on_auto = on_auto
        self.set_auto_timeout()
        self.auto_plan = []

        self.update_plan()

        self.just_parried = False

    def set_auto(self, value):
        self.auto_base_timeout = AUTO_PAUSE if value else None
        self.set_auto_timeout()

    def set_auto_timeout(self):
        if self.auto_base_timeout is None:
            self.auto_timeout = None
        else:
            coeff = 1 + (random() * 0.5)
            self.auto_timeout = self.auto_base_timeout * coeff

    def set_adversary(self, adversary):
        self.adversary = adversary

    def catch_spell(self, spell):
        if not spell.shields:
            self.on_defence_failed(spell)
        else:
            if not self.catched_spells:
                self.set_timeout_on_spell(spell)
                self.on_parry_needed(spell)
                self.update_plan(spell)
            self.catched_spells.append(spell)

    def set_timeout_on_spell(self, spell):
        self.timeout = SHIELD_TIMEOUT if spell.shields else 0

    def remove_top_spell(self):
        self.catched_spells = self.catched_spells[1:]
        if self.catched_spells:
            next_spell = self.catched_spells[0]
            self.set_timeout_on_spell(next_spell)
            self.on_parry_needed(next_spell)
            self.update_plan(next_spell)

    def cast_spell(self, spell):
        if self.catched_spells:
            top_spell = self.catched_spells[0]
            if spell in top_spell.shields:
                self.on_defence_succeded(top_spell)
                self.just_parried = True
                self.remove_top_spell()
                return

        if spell.is_attack and self.adversary is not None:
            self.adversary.catch_spell(spell)
            self.just_parried = False
            if spell.breaks_rull_of_3:
                if (spell in self.attacks_buffer[-2:] and
                   not spell.ignore_rule_of_3):
                    self.on_rule_of_3_failed(spell)
                self.attacks_buffer = (self.attacks_buffer + [spell])[-3:]

    def set_state(self, delta, sequence='', doing_well=False,
                  spell=None, action_timeout=0):
        self.sequence = sequence
        self.doing_well = doing_well
        self.action_timeout = action_timeout
        if spell is not None:
            self.cast_spell(spell)

        if self.catched_spells:
            self.timeout -= delta
            expexted_prefixes = self.catched_spells[0].shields_prefixes
            self.is_defending = self.sequence in expexted_prefixes
            if not self.is_defending and self.timeout < 0:
                top_spell = self.catched_spells[0]
                self.on_defence_failed(top_spell)
                self.remove_top_spell()

        if not doing_well:
            self.update_plan()

        if self.auto_timeout is not None:
            self.auto_timeout -= delta
            if self.auto_timeout < 0:
                self.auto_timeout = -1
                self.auto_action()

    def update_plan(self, to_parry=None):
        if self.auto_base_timeout is None:
            return

        if to_parry is not None:
            if to_parry.shields:
                self.release(AUTO_REACTION)
                self.auto_plan = copy(to_parry.shields[0].sequence)
        elif not self.auto_plan:
            spell = choice([spell for spell in ALL_SPELLS.values()
                            if spell.shields and
                            spell not in self.attacks_buffer])
            timeout = (AUTO_REACTION if self.just_parried else
                       AUTO_PAUSE * random() * 4)
            self.release(timeout)
            self.auto_plan = copy(spell.sequence)

    def release(self, timeout):
        self.on_auto('release')
        self.auto_timeout = timeout

    def auto_action(self):
        if self.auto_base_timeout is not None:
            if self.auto_plan:
                self.on_auto(self.auto_plan.pop(0))
            self.set_auto_timeout()

    def for_gui(self):
        if self.catched_spells and not self.is_defending:
            timeout = int((float(max(self.timeout, 0)) *
                          GUI_MAX_TIMEOUT / SHIELD_TIMEOUT))
        elif self.doing_well:
            timeout = int((float(max(self.action_timeout, 0)) *
                          GUI_MAX_TIMEOUT / ACTION_TIMEOUT))
        else:
            timeout = 0

        return {
            'device_id': self.stick_id,
            'sequence': self.sequence,
            'spells': [spell.name for spell in self.catched_spells],
            'timeout': timeout,
            'attacks_buffer': [spell.key for spell in self.attacks_buffer]
        }
