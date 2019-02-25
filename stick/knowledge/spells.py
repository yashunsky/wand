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
                 breaks_rull_of_3=None,
                 r=0, g=0, b=0, w=0):
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

        self.color = (r, g, b, w)

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
            Spell('DuAuDu', 'Impedimenta', [protego], r=100, g=50),
            Spell('DuHuHs', 'Silencio', [protego], r=50, g=50),
            Spell('DuHuZ', 'Flaguellum', [protego], r=50),
            Spell('HsNZ', 'Incendio', [protego], r=120),
            Spell('HsZN', 'Deluvium', [protego], b=120),

            diffendo,
            Spell('HuDuAu', 'Incarcero', [diffendo], r=50, g=50),
            Spell('HuAuDu', 'Rictusempra', [diffendo], w=255),

            enerveit,
            Spell('AuDuDs', 'Stupefy', [enerveit], r=120),
            Spell('AuNHu', 'Confundus', [enerveit], r=100, g=100),
            Spell('NAuDuHuZ', 'Furore', [enerveit], r=120),

            Spell('HsAsZAuDs', 'Expelliarmus', w=255),

            Spell('NZ', 'Avada Kedavra', ignore_rule_of_3=True, g=255),
            Spell('NHuHs', 'Crucio', ignore_rule_of_3=True, r=255),
            Spell('NAuAs', 'Imperio', ignore_rule_of_3=True, r=255, g=255),
            ]

ALL_SPELLS = {spell.key: spell for spell in get_all_spells()}
ALL_PREFIXES = set(chain(*[spell.prefixes for spell in ALL_SPELLS.values()]))
