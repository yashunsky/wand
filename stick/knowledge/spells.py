#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import chain

from stick_control.position import decode_sequence


def prefixes(sequence):
    prefix = ''
    for position in sequence:
        prefix = prefix + position
        yield prefix


class Spell(object):
    def __init__(self, sequence, name,
                 shields=None, is_attack=True,
                 ignore_rule_of_3=False,
                 breaks_rull_of_3=None):
        super(Spell, self).__init__()

        if isinstance(shields, Spell):
            shields = [shields]

        self.name = name
        self.key = sequence
        self.sequence = decode_sequence(sequence)
        self.shields = [] if shields is None else shields
        self.prefixes = set(prefixes(self.sequence))
        self.shields_prefixes = set(chain(*[spell.prefixes
                                            for spell in self.shields]))
        self.is_attack = is_attack
        self.ignore_rule_of_3 = ignore_rule_of_3
        self.breaks_rull_of_3 = (is_attack if breaks_rull_of_3 is None
                                 else breaks_rull_of_3)

        self.audio_key = name.lower().replace(' ', '_')

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def get_all_spells():
    # shields
    protego = Spell('DuZDu', 'Protego', is_attack=False)
    diffendo = Spell('HuZHu', 'Diffendo', is_attack=False)
    enerveit = Spell('AuZAu', 'Enerveit', is_attack=False)

    return [protego,
            Spell('DuAuDu', 'Impedimenta', [protego]),
            Spell('DuHuHs', 'Silencio', [protego]),
            Spell('DuHuZ', 'Flaguellum', [protego]),
            Spell('HsNZ', 'Incendio', [protego]),
            Spell('HsZN', 'Deluvium', [protego]),

            diffendo,
            Spell('HuDuAu', 'Incarcero', [diffendo]),
            Spell('HuAuDu', 'Rictusempra', [diffendo]),

            enerveit,
            Spell('AuDuDs', 'Stupefy', [enerveit]),
            Spell('AuNHu', 'Confundus', [enerveit]),
            Spell('NAuDuHuZ', 'Furore', [enerveit]),

            Spell('HsAsZAuDs', 'Expelliarmus'),

            Spell('NZ', 'Avada Kedavra', ignore_rule_of_3=True),
            Spell('NHuHs', 'Crucio', ignore_rule_of_3=True),
            Spell('NAuAs', 'Imperio', ignore_rule_of_3=True),
            ]

ALL_SPELLS = {spell.key: spell for spell in get_all_spells()}
ALL_PREFIXES = set(chain(*[spell.prefixes for spell in ALL_SPELLS.values()]))
