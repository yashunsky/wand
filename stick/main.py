#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from uart_reader import UartReader
from setup import PORT, OFFSETS
from raw_processor import RawToSequence
from duellist import Duellist


def on_defence_succeded(duellist_name, attack_spell, shield):
    print('Дуэлянт %s отбил %s, скастовав %s' %
          (duellist_name, attack_spell, shield))


def on_defence_failed(duellist_name, spell):
    print('Дуэлянт %s не отбил %s' % (duellist_name, spell))


def on_rule_of_3_failed(duellist_name, spell):
    print('Дуэлянт %s нарушил правило 3х скастовав %s' %
          (duellist_name, spell))

if __name__ == '__main__':
    raw_stream = UartReader(serial_port=PORT)

    raw_processors = {device_id: RawToSequence(offsets['A'], offsets['G'])
                      for device_id, offsets in OFFSETS.items()}

    a = Duellist(0,
                 lambda a, d: on_defence_succeded('А', a, d),
                 lambda s: on_defence_failed('А', s),
                 lambda s: on_rule_of_3_failed('А', s))

    b = Duellist(1,
                 lambda a, d: on_defence_succeded('Б', a, d),
                 lambda s: on_defence_failed('Б', s),
                 lambda s: on_rule_of_3_failed('Б', s))

    a.set_adversary(b)
    b.set_adversary(a)

    duellists = {d.stick_id: d for d in (a, b)}

    prev_sequence = ''

    # for immediate attack
    # b.cast_spell(ALL_SPELLS['DuHuHs'])

    for raw_data in raw_stream():
        raw_to_sequence = raw_processors[raw_data['device_id']]
        duellist = duellists[raw_data['device_id']]

        state = raw_to_sequence(raw_data)

        duellist.set_state(state['delta'], state['sequence'], state['vibro'],
                           state['spell'] if state['done'] else None)

        if state['done'] or state['sequence'] != prev_sequence:
            del state['delta']
            state['spell_time'] = '%2.1f' % state['spell_time']
            print(state)
        prev_sequence = state['sequence']
