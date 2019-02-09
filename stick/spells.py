#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


from position import decode_sequence


class Spell(object):
    def __init__(self, sequence, name, shields=None):
        super(Spell, self).__init__()

        if isinstance(shields, Spell):
            shields = [shields]

        self.name = name
        self.sequence = decode_sequence(sequence)
        self.shields = [] if shields is None else shields

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def get_all_spells():
    # shields
    protego = Spell('DuZDu', 'Протего')
    diffendo = Spell('HuZHu', 'Диффендо')
    enerveit = Spell('AuZAu', 'Щит Энервейт')
    tabula_rasa = Spell('DsAuDuAsHu', 'Табула Раса')

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
            Spell('NZ', 'Авада Кедавра'),
            Spell('NHuHs', 'Круцио'),
            Spell('NAuAs', 'Империо'),
            Spell('ZAuAsAuZ', 'Экзорцио', tabula_rasa),
            Spell('DdDsDdDuDs', 'Чара, завершающая зельеварение')]
