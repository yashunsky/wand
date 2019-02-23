#!/usr/local/bin/python3
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
                 accusative=None,
                 audio_key=None):
        super(Spell, self).__init__()

        if isinstance(shields, Spell):
            shields = [shields]

        self.name = name
        self.accusative = name if accusative is None else accusative
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

        self.audio_key = audio_key

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def get_all_spells():
    # shields
    protego = Spell('DuZDu', 'Протего', is_attack=False)
    diffendo = Spell('HuZHu', 'Диффендо', is_attack=False)
    enerveit = Spell('AuZAu', 'Энервейт', is_attack=False)

    return [protego,
            Spell('DuAuDu', 'Импедимента', [protego], audio_key='impedimenta',
                  accusative='Импедименту'),
            Spell('DuHuHs', 'Силенцио', [protego], audio_key='silencio'),
            Spell('DuHuZ', 'Флагелум', [protego], audio_key='flaguelum'),
            Spell('HsNZ', 'Инсендио', [protego], audio_key='incendio'),
            Spell('HsZN', 'Делювиум', [protego], audio_key='deluvium'),

            diffendo,
            Spell('HuDuAu', 'Инкарцеро', [diffendo], audio_key='incarcero'),
            Spell('HuAuDu', 'Риктусемпра', [diffendo], audio_key='rictusempra',
                  accusative='Риктусемпру'),

            enerveit,
            Spell('AuDuDs', 'Ступефай', [enerveit], audio_key='stupefy'),
            Spell('AuNHu', 'Конфундус', [enerveit], audio_key='confundus'),
            Spell('NAuDuHuZ', 'Фуроре', [enerveit], audio_key='furore'),

            Spell('HsAsZAuDs', 'Экспеллиармус', audio_key='expelliarmus'),

            Spell('NZ', 'Авада Кедавра', ignore_rule_of_3=True,
                  accusative='Аваду Кедавру', audio_key='avada_kedavra'),
            Spell('NHuHs', 'Круцио', ignore_rule_of_3=True,
                  audio_key='crucio'),
            Spell('NAuAs', 'Империо', ignore_rule_of_3=True,
                  audio_key='imperio'),
            ]

ALL_SPELLS = {spell.key: spell for spell in get_all_spells()}
ALL_PREFIXES = set(chain(*[spell.prefixes for spell in ALL_SPELLS.values()]))
