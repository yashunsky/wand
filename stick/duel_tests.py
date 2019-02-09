#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import unittest

from duellist import Duellist
from spells import ALL_SPELLS

SILENCIO = ALL_SPELLS['DuHuHs']
IMPEDIMENTA = ALL_SPELLS['DuAuDu']
RICTUSEMPRA = ALL_SPELLS['HuAuDu']

PROTEGO = ALL_SPELLS['DuZDu']
DIFFENDO = ALL_SPELLS['HuZHu']

INSENDIO = ALL_SPELLS['HsNZ']
DELUVIUM = ALL_SPELLS['HsZN']


class DuelTest(unittest.TestCase):

    def setUp(self):
        self.a = Duellist(0)
        self.b = Duellist(1)

        self.a.set_adversary(self.b)
        self.b.set_adversary(self.a)

    def test_non_defended(self):
        passed_to_b = []
        self.b.on_defence_failed = lambda s: passed_to_b.append(s)

        # a attacks b
        self.a.set_state(0.1, spell=SILENCIO)

        # b does nothing
        self.b.set_state(10.0)
        assert passed_to_b == [SILENCIO]

    def test_attack_defence(self):
        passed_to_b = []
        self.b.on_defence_failed = lambda s: passed_to_b.append(s)

        # a attacks b twice
        self.a.set_state(0.1, spell=SILENCIO)
        self.a.set_state(0.1, spell=IMPEDIMENTA)
        assert self.b.catched_spells == [SILENCIO, IMPEDIMENTA]

        # b parries first spell
        self.b.set_state(0.1, spell=PROTEGO)
        assert self.b.catched_spells == [IMPEDIMENTA]
        assert passed_to_b == []

        # b missparries second spell and it passes
        self.b.set_state(10, spell=DIFFENDO)
        assert self.b.catched_spells == []
        assert passed_to_b == [IMPEDIMENTA]

    def test_started_defence(self):
        passed_to_b = []
        self.b.on_defence_failed = lambda s: passed_to_b.append(s)

        # a attacks b
        self.a.set_state(0.1, spell=SILENCIO)
        assert self.b.catched_spells == [SILENCIO]

        # b starts quickly a very long defence...
        self.b.set_state(0.1, sequence='Ds')
        assert passed_to_b == []
        self.b.set_state(5.0, sequence='DsAu')
        assert passed_to_b == []
        self.b.set_state(5.0, sequence='DsAuDu')
        assert passed_to_b == []
        # ...but fails it
        self.b.set_state(5.0, sequence='DsAuDuAu')
        assert passed_to_b == [SILENCIO]

    def test_rule_3_basic_failure(self):
        rule_of_3_failure = []
        self.a.on_rule_of_3_failed = lambda s: rule_of_3_failure.append(s)

        # a knows only one spell
        self.a.set_state(0.1, spell=SILENCIO)
        self.a.set_state(0.1, spell=SILENCIO)

        assert rule_of_3_failure == [SILENCIO]

    def test_rule_3_failure(self):
        rule_of_3_failure = []
        self.a.on_rule_of_3_failed = lambda s: rule_of_3_failure.append(s)

        # a knows 3 spells...
        self.a.set_state(0.1, spell=SILENCIO)
        self.a.set_state(0.1, spell=IMPEDIMENTA)
        self.a.set_state(0.1, spell=RICTUSEMPRA)
        self.a.set_state(0.1, spell=SILENCIO)
        assert rule_of_3_failure == []

        # but forgets what he just did
        self.a.set_state(0.1, spell=RICTUSEMPRA)
        assert rule_of_3_failure == [RICTUSEMPRA]

    def test_water_and_fire(self):
        rule_of_3_failure = []
        self.b.on_rule_of_3_failed = lambda s: rule_of_3_failure.append(s)

        # a attacks with water
        self.a.set_state(0.1, spell=DELUVIUM)
        assert self.b.catched_spells == [DELUVIUM]
        # b parries with fire...
        self.b.set_state(0.1, spell=INSENDIO)
        assert self.a.catched_spells == []
        assert self.b.catched_spells == []

        # ...and strikes back. the rull of three does'nt count for defences
        self.b.set_state(0.1, spell=INSENDIO)
        assert self.a.catched_spells == [INSENDIO]
        assert rule_of_3_failure == []


if __name__ == '__main__':
    unittest.main()
