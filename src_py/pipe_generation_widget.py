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

DISPLAY_STATES = {'calibration': {'bg': 'white', 'fg': 'black',
                                  'message': u'идет калибровка'},
                  'idle': {'bg': 'white', 'fg': 'black',
                           'message': u'ждём жеста'},
                  'splitting': {'bg': 'white', 'fg': 'black',
                                'message': u'жест'},
                  'demo': {'bg': 'white', 'fg': 'black',
                           'message': u'жест похож на'},
                  'done_sequence': {'bg': 'white', 'fg': 'black',
                                          'message':
                                          u'выполнена'},
                  'in_progress': {'bg': 'white', 'fg': 'black',
                                  'message': u'выполнен'}}


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

        self.display_state = ''

        self.pop_up = False

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

    def set_state(self, new_display_state, subtitle=''):
        if new_display_state not in DISPLAY_STATES:
            return

        self.display_state = new_display_state
        if self.pop_up:
            return

        display_state = DISPLAY_STATES[self.display_state]
        self.set_color(display_state['bg'], display_state['fg'])
        self.set_message(display_state['message'])
        self.set_subtitle(subtitle)

        if 'train' in self.display_state:
            self.button.show()
        else:
            self.button.hide()
