#!/usr/bin/env python
#-*- coding: utf-8 -*-

'''Look at the strokes, select the best and make a core out of them'''

from PySide.QtGui import QApplication, QWidget
from PySide.QtGui import QLabel, QTextEdit, QGridLayout, QComboBox, QListView
from PySide.QtGui import QPushButton, QCheckBox, QLineEdit
from PySide.QtCore import QAbstractListModel
from PySide.QtCore import Qt

import sys
import numpy as np
import pyqtgraph as pg

from os.path import join, isfile, basename
from os import listdir


def get_letters(path):
    '''Read stroke files from given folder
    and arange them into a dict of lists by key-letter'''
    files = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    letters = {}
    for f in files:
        data = np.loadtxt(f)
        filename = basename(f)
        key = filename[0]
        if not key in letters:
            letters[key] = []
        letters[key].append({'filename': filename, 'data':data})
    return letters

def stereographic(x, y, z):
    '''Transform 3D coords into 2D
    using stereographic projection'''
    return x/(1+y), -z/(1+y)

class StrokeList(QAbstractListModel):
    """Model, containing strokes and there curve-representation"""
    def __init__(self, strokes, plot):
        super(StrokeList, self).__init__()
        self.strokes = strokes
        self.plot = plot

        for letter_group in self.strokes.values():
            for letter in letter_group:
                letter['checked'] = Qt.Checked
                x, y = stereographic(letter['data'][:, 0],
                                     letter['data'][:, 1],
                                     letter['data'][:, 2])
                pen = pg.mkPen(width=10, color=(0,0,255,50))
                pen.setCapStyle(Qt.RoundCap)
                letter['curve'] = pg.PlotCurveItem(x=x, y=y, pen=pen)
                letter['curve'].setVisible(False)
                self.plot.addItem(letter['curve'])
        self.stroke_group = []
        self.key_letter = ''


    def set_key_letter(self, letter):
        '''Select one list by key-letter'''
        # Choose the right list from the strokes dict

        self.key_letter = letter
        if self.key_letter in self.strokes:
            self.stroke_group = self.strokes[self.key_letter]
        else:
            self.stroke_group = []

        # hide all curves, the ones who need to be shown
        # will be reset visible on modelReset 

        for letter_group in self.strokes.values():
            for letter in letter_group:
                letter['curve'].setVisible(False)
        
        # reset model so changes become visivle
        self.modelReset.emit()

    def rowCount(self, *args):
        return len(self.stroke_group)

    def data(self, index, role):
        row = index.row()
        # show stroke filename for display
        if role == Qt.DisplayRole:
            return self.stroke_group[row]['filename']

        elif role == Qt.CheckStateRole:
            # Change curve visibility
            # according to stroke 'checked' status
            visible = self.stroke_group[row]['checked'] == Qt.Checked
            self.stroke_group[row]['curve'].setVisible(visible)
            return self.stroke_group[row]['checked']
        else:
            return None

    def setData(self, index, value, role):
        # Update stroke 'checked' status 
        row = index.row()
        if role == Qt.CheckStateRole:
             self.stroke_group[row]['checked'] = value
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled

class CoreCreator(QWidget):
    """Main module's widget"""
    def __init__(self, path):
        super(CoreCreator, self).__init__()
        self.setup_ui()
        self.stroke_list = StrokeList(get_letters(path), self.display)



        self.letter_selector.addItems(['_'] + self.stroke_list.strokes.keys())
        self.list_view.setModel(self.stroke_list)

        self.letter_selector.currentIndexChanged.connect(self.select_letter)

    def select_letter(self):
        # set stroke_list key_letter to the one
        # choosen by letter_selector
        new_letter = self.letter_selector.currentText()
        self.stroke_list.set_key_letter(new_letter)

    def setup_ui(self):
        self.resize(800, 480)
        self.grid = QGridLayout(self)

        self.display = pg.PlotWidget(name='st', background='w') 
        self.grid.addWidget(self.display, 0, 0, 2, 2)

        self.display.getViewBox().setXRange(-np.pi, np.pi)
        self.display.getViewBox().setYRange(-np.pi/2, np.pi/2)
        self.display.getViewBox().setAspectLocked()

        self.list_view = QListView(self)
        self.grid.addWidget(self.list_view, 0, 2, 1, 2)

        self.letter_selector = QComboBox(self)
        self.grid.addWidget(self.letter_selector, 1, 2, 1, 2)

        self.relative_chk = QCheckBox(self)
        self.relative_chk.setText('Relative coords')
        self.grid.addWidget(self.relative_chk, 2, 0, 1, 1)

        self.create_core_btn = QPushButton(self)
        self.create_core_btn.setText('Create core')
        self.grid.addWidget(self.create_core_btn, 2, 1, 1, 1)

        self.letter_edt = QLineEdit(self)
        self.grid.addWidget(self.letter_edt, 2, 2, 1, 1)

        self.set_letter_btn = QPushButton(self)
        self.set_letter_btn.setText('Set')
        self.grid.addWidget(self.set_letter_btn, 2, 3, 1, 1)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)

    cc = CoreCreator('learned')

    cc.show()

    sys.exit(app.exec_())