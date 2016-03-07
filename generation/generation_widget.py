#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget, QLabel, QPushButton
from PyQt4.QtGui import QGridLayout, QFont
from PyQt4.QtCore import QTimer

from PyQt4.QtCore import Qt

DEFAULT_FONT_SIZE = 80
DEFAULT_FG_COLOR = 'black'
DEFAULT_BG_COLOR = 'white'

FONT_FAMILY = 'Sans'
START_MESSAGE = u'Поколение'
START_SUBTITLE = u''
WIDTH = 500
HEIGHT = 500

PROCESS_INTERVAL = 100

STATES = {'calibration': {'bg': 'white', 'fg': 'black',
                          'message': u'идет калибровка'},
          'wait_for_init': {'bg': 'white', 'fg': 'black',
                            'message': u'ждём жеста инициации'},
          'init_done': {'bg': 'white', 'fg': 'black',
                        'message': u'жест инициации выполнен'},
          'wait_for_definition': {'bg': 'white', 'fg': 'black',
                                  'message': u'ждём определяющего жеста'},
          'definition_done': {'bg': 'white', 'fg': 'black',
                              'message': u'определяющий жест выполнен'},
          'wait_for_activate': {'bg': 'white', 'fg': 'black',
                                'message': u'ждём жеста активации'},
          'activation_done': {'bg': 'white', 'fg': 'black',
                              'message': u'активация выполнена'},
          'wait_for_train': {'bg': 'white', 'fg': 'black',
                             'message': u'ждём жеста для сохранения'},
          'train_in_progress': {'bg': 'white', 'fg': 'black',
                                'message': u'жест выполняется'},
          'train_done': {'bg': 'white', 'fg': 'black',
                         'message': u'жест сохранен'},
          'wait_for_demo': {'bg': 'white', 'fg': 'black',
                            'message': u'ждём любого жеста'},
          'demo_in_progress': {'bg': 'white', 'fg': 'black',
                               'message': u'жест выполняется'},
          'demo_done': {'bg': 'white', 'fg': 'black',
                        'message': u'жест распознан'}}


class GenerationWidget(QWidget):
    def __init__(self):
        super(GenerationWidget, self).__init__()

        self.grid = QGridLayout(self)

        self.resize(WIDTH, HEIGHT)

        self.font = QFont()
        self.font.setFamily(FONT_FAMILY)

        self.message = QLabel(self)
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setFont(self.font)

        self.subtitle = QLabel(self)
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setFont(self.font)

        self.grid.addWidget(self.message, 0, 0, 1, 1)
        self.grid.addWidget(self.subtitle, 1, 0, 1, 1)

        self.set_color(DEFAULT_BG_COLOR, DEFAULT_FG_COLOR)
        self.set_message(START_MESSAGE)
        self.set_subtitle(START_SUBTITLE)

        self.button = QPushButton(self)
        self.button.setText(u'следующий жест')
        self.button.clicked.connect(self.next_stroke)

        self.grid.addWidget(self.button, 2, 0, 1, 1)

        self.state = ''

        self.main_timer = QTimer()
        self.main_timer.setInterval(PROCESS_INTERVAL)
        self.main_timer.timeout.connect(self.process)
        self.main_timer.start()

    def next_stroke(self):
        pass

    def process(self):
        pass

    def set_color(self, bg_color, fg_color):
        self.setStyleSheet('background-color: {bg}; color: {fg};'
                           .format(bg=bg_color, fg=fg_color))

    def set_message(self, text, font_size=DEFAULT_FONT_SIZE):
        self.font.setPixelSize(font_size)
        self.message.setFont(self.font)
        self.message.setText(text)

    def set_subtitle(self, text, font_size=DEFAULT_FONT_SIZE):
        self.font.setPixelSize(font_size)
        self.subtitle.setFont(self.font)
        self.subtitle.setText(text)

    def set_state(self, new_state, subtitle=''):
        if new_state not in STATES:
            return

        self.state = new_state
        state = STATES[self.state]
        self.set_color(state['bg'], state['fg'])
        self.set_message(state['message'])
        self.set_subtitle(subtitle)

        if 'train' in self.state:
            self.button.show()
        else:
            self.button.hide()

    def reset_state(self, target_state, delay):
        origin_state = self.state

        def on_timer():
            if self.state == origin_state:
                self.set_state(target_state)
                self.reset_timer.stop()

        self.reset_timer = QTimer()
        self.reset_timer.setInterval(delay * 1000)
        self.reset_timer.timeout.connect(on_timer)
        self.reset_timer.start()
