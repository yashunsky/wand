#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from itertools import chain
from position import decode_sequence


def prefixes(sequence):
    prefix = ''
    for position in sequence:
        prefix = prefix + position
        yield prefix


class Spell(object):
    def __init__(self, sequence, name,
                 shields=None, is_attack=True,
                 ignore_rule_of_3=False):
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def get_all_spells():
    # shields
    protego = Spell('DuZDu', 'Протего', is_attack=False)
    diffendo = Spell('HuZHu', 'Диффендо', is_attack=False)
    enerveit = Spell('AuZAu', 'Щит Энервейт', is_attack=False)
    tabula_rasa = Spell('DsAuDuAsHu', 'Табула Раса', is_attack=False)

    # cyclic linked spells
    insendio = Spell('HsNZ', 'Инсендио')
    deluvium = Spell('HsZN', 'Делювиум', [insendio, tabula_rasa])
    insendio.shields = [deluvium, tabula_rasa]

    return [protego,
            Spell('DuAuDu', 'Импедимента', [protego, tabula_rasa]),
            Spell('DuHuHs', 'Силенцио', [protego, tabula_rasa]),
            Spell('DuHuZ', 'Режущее заклятие', [protego, tabula_rasa]),

            diffendo,
            Spell('HuDuAu', 'Инкарцеро', [diffendo, tabula_rasa]),
            Spell('HuAuDu', 'Риктусемпра', [diffendo, tabula_rasa]),

            enerveit,
            Spell('AuDuDs', 'Ступефай', [enerveit, tabula_rasa]),
            Spell('AuNHu', 'Конфундус', [enerveit, tabula_rasa]),
            Spell('NAuDuHuZ', 'Отложенная смерть', [enerveit, tabula_rasa]),

            insendio,
            deluvium,

            Spell('HsAsZAuDs', 'Экспеллиармус', tabula_rasa),
            tabula_rasa,
            Spell('NZ', 'Авада Кедавра', ignore_rule_of_3=True),
            Spell('NHuHs', 'Круцио'),
            Spell('NAuAs', 'Империо'),
            Spell('ZAuAsAuZ', 'Экзорцио', tabula_rasa),
            Spell('DdDsDdDuDs', 'Чара, завершающая зельеварение',
                  is_attack=False)]

ALL_SPELLS = {spell.key: spell for spell in get_all_spells()}
ALL_PREFIXES = set(chain(*[spell.prefixes for spell in ALL_SPELLS.values()]))

AVADA = ALL_SPELLS['NZ']
