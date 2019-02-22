#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
from random import choice, shuffle
import sys
import tkinter as tk


from gui import Ring
from mages import Mage
from data_injector import DataInjector
from setup import OFFSETS
from raw_processor import RawToSequence
from duellist import Duellist
from spells import ALL_SPELLS


def start_gui(duellists, pipe_in, pipe_out, play_audio):
    Ring(duellists, pipe_in, pipe_out, 'Agatha-Modern', play_audio)
    tk.mainloop()


def start_main_thread(keyboard_input, pipe_in, pipe_out):
    injected_ids = [0, 1] if keyboard_input else [1]

    raw_stream = (DataInjector(ids=injected_ids) if keyboard_input
                  else UartReader(injected_ids=injected_ids))

    if isinstance(raw_stream, DataInjector):
        raw_stream.init_device(0)
        raw_stream.init_device(1)

    raw_processors = {device_id: RawToSequence(offsets['A'], offsets['G'])
                      for device_id, offsets in OFFSETS.items()}

    duellists = {}

    def send(device_id, popup_type, spells):
        message_to_send = {'device_id': device_id,
                           'popup_type': popup_type,
                           'spells': spells}
        pipe_out.send(message_to_send)

        duellist = duellists[device_id]
        pipe_out.send(duellist.for_gui())

    a = Duellist(0,
                 lambda s: send(0, 'parry_needed', s),
                 lambda a, d: send(0, 'defence_succeded', [a, d]),
                 lambda s: send(0, 'defence_failed', s),
                 lambda s: send(0, 'rule_of_3_failed', s),
                 lambda s: send(0, 'death', s))

    b = Duellist(1,
                 lambda s: send(1, 'parry_needed', s),
                 lambda a, d: send(1, 'defence_succeded', [a, d]),
                 lambda s: send(1, 'defence_failed', s),
                 lambda s: send(1, 'rule_of_3_failed', s),
                 lambda s: send(1, 'death', s))

    a.set_adversary(b)
    b.set_adversary(a)

    for d in (a, b):
        duellists[d.stick_id] = d

    messages = {}

    for raw_data in raw_stream():
        if pipe_in.poll():
            message = pipe_in.recv()
            if 'device_id' in message and message['device_id'] is None:
                if message['position'] == 'random':
                    duellist = choice(duellists)
                    last_catched = duellist.catched_spells[-3:]
                    spells = [spell for spell in ALL_SPELLS.values()
                              if spell.shields and (spell not in last_catched)]
                    duellist.catch_spell(choice(spells))
            else:
                raw_stream.process_action(message)
        if raw_data is None:
            continue

        raw_to_sequence = raw_processors[raw_data['device_id']]
        duellist = duellists[raw_data['device_id']]

        state = raw_to_sequence(raw_data)

        if raw_data['device_id'] in injected_ids:
            raw_stream.set_inner_feedback(raw_data['device_id'], state)

        duellist.set_state(state['delta'], state['sequence'], state['vibro'],
                           state['spell'] if state['done'] else None,
                           state['action_timeout'])

        for duellist in duellists.values():
            message_to_send = duellist.for_gui()
            if message_to_send not in messages.values():
                pipe_out.send(message_to_send)
                messages[message_to_send['device_id']] = message_to_send


if __name__ == '__main__':
    from_gui_parent, from_gui_child = Pipe(duplex=False)
    to_gui_parent, to_gui_child = Pipe(duplex=False)

    keys = sys.argv[1:]

    use_uart = '-u' in keys
    play_audio = '-a' in keys

    if use_uart:
        from uart_reader import UartReader

    keyboard_input = not use_uart

    duellists = [choice([Mage.ROWENA, Mage.HELGA]),
                 choice([Mage.GODRIC, Mage.SALAZAR])]

    shuffle(duellists)

    p = Process(target=start_main_thread,
                args=(keyboard_input, from_gui_parent, to_gui_child))
    p.start()
    start_gui(duellists, to_gui_parent, from_gui_child, play_audio)
    p.join()
