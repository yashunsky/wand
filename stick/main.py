#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
import sys
import tkinter as tk


from gui import Ring
from mages import Mage
from uart_reader import UartReader
from data_injector import DataInjector
from setup import OFFSETS
from raw_processor import RawToSequence
from duellist import Duellist


def start_gui(duellists, pipe_in, pipe_out):
    Ring(duellists, pipe_in, pipe_out)
    tk.mainloop()


def on_defence_succeded(duellist_name, attack_spell, shield):
    print('Дуэлянт %s отбил %s, скастовав %s' %
          (duellist_name, attack_spell, shield))


def on_defence_failed(duellist_name, spell):
    print('Дуэлянт %s не отбил %s' % (duellist_name, spell))


def on_rule_of_3_failed(duellist_name, spell):
    print('Дуэлянт %s нарушил правило 3х скастовав %s' %
          (duellist_name, spell))


def start_main_thread(keyboard_input, pipe_in, pipe_out):
    raw_stream = DataInjector() if keyboard_input else UartReader()

    if isinstance(raw_stream, DataInjector):
        raw_stream.init_device(0)
        raw_stream.init_device(1)

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

    messages = {}

    for raw_data in raw_stream():
        if pipe_in.poll():
            raw_stream.process_action(pipe_in.recv())
        if raw_data is None:
            continue

        raw_to_sequence = raw_processors[raw_data['device_id']]
        duellist = duellists[raw_data['device_id']]

        state = raw_to_sequence(raw_data)

        if keyboard_input:
            raw_stream.set_feedback(raw_data['device_id'], state)

        duellist.set_state(state['delta'], state['sequence'], state['vibro'],
                           state['spell'] if state['done'] else None,
                           state['action_timeout'])

        for duellist in duellists.values():
            message_to_send = duellist.for_gui()
            if message_to_send not in messages.values():
                pipe_out.send(message_to_send)
                messages[raw_data['device_id']] = message_to_send

        # if state['done'] or state['sequence'] != prev_sequence:
        #     del state['delta']
        #     state['spell_time'] = '%2.1f' % state['spell_time']
        #     pipe_out.send({
        #         'device_id': raw_data['device_id'],
        #         'sequence': state['sequence']
        #     })
        #     print(state)
        # prev_sequence = state['sequence']


if __name__ == '__main__':
    from_gui_parent, from_gui_child = Pipe(duplex=False)
    to_gui_parent, to_gui_child = Pipe(duplex=False)

    keyboard_input = len(sys.argv) > 1 and sys.argv[1] == '-k'

    duellists = [Mage.MOLLY, Mage.BELLATRIX]

    p = Process(target=start_main_thread,
                args=(keyboard_input, from_gui_parent, to_gui_child))
    p.start()
    start_gui(duellists, to_gui_parent, from_gui_child)
    p.join()
