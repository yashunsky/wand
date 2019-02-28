#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multiprocessing import Process, Pipe
from random import choice, shuffle
import sys
import tkinter as tk


from duellist import Duellist
from gui.ring import Ring
from knowledge.mages import Mage
from knowledge.setup import OFFSETS
from knowledge.spells import ALL_SPELLS
from stick_control.pulse_generator import PulseGenerator
from stick_control.raw_processor import RawToSequence


def start_gui(duellists, pipe_in, pipe_out, play_audio):
    Ring(duellists, pipe_in, pipe_out, 'Agatha-Modern', play_audio)
    tk.mainloop()


def start_main_thread(keyboard_input, pipe_in, pipe_out):
    injected_ids = [0, 1] if keyboard_input else []

    raw_stream = (PulseGenerator(ids=injected_ids) if keyboard_input
                  else UartReader(injected_ids=injected_ids))

    raw_processors = {device_id: RawToSequence(offsets['A'], offsets['G'])
                      for device_id, offsets in OFFSETS.items()}

    duellists = {}

    def send(device_id, popup_type, spell):
        message_to_send = {'device_id': device_id,
                           'popup_type': popup_type,
                           'spell': spell}
        pipe_out.send(message_to_send)

        duellist = duellists[device_id]
        pipe_out.send(duellist.for_gui())

    a = Duellist(0,
                 lambda s: send(0, 'parry_needed', s),
                 lambda s: send(0, 'defence_succeded', s),
                 lambda s: send(0, 'defence_failed', s),
                 lambda s: send(0, 'rule_of_3_failed', s),
                 lambda p: raw_processors[0].inject(p))

    b = Duellist(1,
                 lambda s: send(1, 'parry_needed', s),
                 lambda s: send(1, 'defence_succeded', s),
                 lambda s: send(1, 'defence_failed', s),
                 lambda s: send(1, 'rule_of_3_failed', s),
                 lambda p: raw_processors[1].inject(p))

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
            elif message['action'] == 'auto':
                duellists[message['device_id']].set_auto(message['value'])
            elif message['action'] == 'position':
                raw_processors[message['device_id']].inject(message['position'])
            elif message['action'] == 'exit':
                raw_stream.stop()

        raw_to_sequence = raw_processors[raw_data['device_id']]
        duellist = duellists[raw_data['device_id']]

        state = raw_to_sequence(raw_data)

        raw_stream.set_feedback(raw_data['device_id'], **state['feedback'])

        duellist.set_state(state['delta'], state['sequence'],
                           state['doing_well'],
                           state['spell'],
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
        from stick_control.uart_reader import UartReader

    keyboard_input = not use_uart

    mages = list(Mage)
    shuffle(mages)
    duellists = mages[:2]

    p = Process(target=start_main_thread,
                args=(keyboard_input, from_gui_parent, to_gui_child))
    p.start()
    start_gui(duellists, to_gui_parent, from_gui_child, play_audio)
    p.join()
