#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Look at the strokes, select the best and make a core out of them'''

import json
import sys
from os.path import join, basename
from os import rename, walk

from PyQt4.QtCore import QAbstractListModel
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QWidget, QGridLayout, QComboBox
from PyQt4.QtGui import QPushButton, QLineEdit, QListView

import numpy as np
import pyqtgraph as pg
from unify_definition import unify_stroke


SEGMENTATION = 128

CORE_NAME = '../generation.json'


def make_core(letters, points):
    core = {}
    for key, letters_group in letters.items():
        unified = np.array([unify_stroke(letter, points)
                            for letter in letters_group])
        centers = np.mean(unified, axis=0)

        n = np.linalg.norm(centers, axis=1)

        norms = np.vstack((n, n, n)).T

        centers = centers / norms

        core[key] = centers
    return core


def get_letters(path):
    '''Read stroke files from given folder
    and arange them into a dict of lists by key-letter'''

    letters = {}

    for (dirpath, dirnames, filenames) in walk(path):
        if dirpath == path:
            continue
        for f in filenames:
            try:
                data = np.loadtxt(join(dirpath, f))
            except ValueError:
                continue
            filename = basename(f)
            key = dirpath.split('/')[-1].split('-')[0]
            if key not in letters:
                letters[key] = []
            letters[key].append({'filename': filename, 'data': data})
    return letters


def stereographic(x, y, z):
    '''Transform 3D coords into 2D
    using stereographic projection'''
    return -x / (1 - y), z / (1 - y)


def add_circles(plot, radiuses, segmentation=32):
    '''Draw concentric circles on given plot'''
    pen = pg.mkPen(width=1, color=(0, 0, 0, 50))
    angles = np.linspace(0, 2 * np.pi, segmentation)
    angles = np.hstack((angles, np.zeros(1)))
    x = np.cos(angles)
    y = np.sin(angles)
    for r in radiuses:
        circle_curve = pg.PlotCurveItem(x=x * r, y=y * r, pen=pen)
        plot.addItem(circle_curve)


class KeyList(QAbstractListModel):
    def __init__(self, keys):
        super(KeyList, self).__init__()
        self.keys = [''] + keys

    def set_keys(self, keys):
        self.keys = [''] + keys
        self.modelReset.emit()

    def rowCount(self, *args):
        return len(self.keys)

    def data(self, index, role):
        row = index.row()
        # show stroke filename for display
        if role == Qt.DisplayRole:
            return self.keys[row]
        else:
            return None


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
                pen = pg.mkPen(width=10, color=(0, 0, 255, 50))
                pen.setCapStyle(Qt.RoundCap)
                letter['curve'] = pg.PlotCurveItem(x=x, y=y, pen=pen)
                letter['curve'].setVisible(False)
                self.plot.addItem(letter['curve'])
        self.stroke_group = []
        self.key_letter = ''

        self.preview_stroke = pg.PlotCurveItem()
        self.plot.addItem(self.preview_stroke)

        self.set_preview(reset=True)

        self.keys_model = KeyList(self.strokes.keys())

    def make_preview(self):
        preview = None
        letters = self.make_dict(all_letters=False)

        preview_set = make_core(letters, SEGMENTATION)
        if self.key_letter in preview_set:
            preview = preview_set[self.key_letter]
        return preview

    def set_preview(self, reset=False):

        pen = pg.mkPen(width=5, color=(255, 0, 0, 255))
        pen.setCapStyle(Qt.RoundCap)

        if reset:
            x = y = np.array([0])
        else:
            preview = self.make_preview()
            if preview is None:
                return
            x, y = stereographic(preview[:, 0],
                                 preview[:, 1],
                                 preview[:, 2])
        self.preview_stroke.setData(x=x, y=y, pen=pen)

    def make_dict(self, all_letters=True):
        return {key: [element['data'] for element in elements_list
                      if element['checked'] == Qt.Checked]
                for key, elements_list in self.strokes.items()
                if all_letters or key == self.key_letter}

    def set_key_letter(self, letter):
        '''Select one list by key-letter'''
        # Choose the right list from the strokes dict

        self.key_letter = str(letter)
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
        self.set_preview(reset=False)

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
            self.set_preview()
        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled

    def change_stroke_key(self, index, new_key, path):
        row = index.row()
        data = self.stroke_group[row]

        del self.strokes[self.key_letter][row]
        if not self.strokes[self.key_letter]:
            del self.strokes[self.key_letter]
            self.key_letter = ''
        if new_key not in self.strokes:
            self.strokes[new_key] = []
        self.strokes[new_key].append(data)

        new_filename = new_key + data['filename'][1:]
        rename(join(path, data['filename']), join(path, new_filename))
        data['filename'] = new_filename

        self.set_key_letter(self.key_letter)

        self.keys_model.set_keys(self.strokes.keys())


class CoreCreator(QWidget):
    """Main module's widget"""
    def __init__(self, path):
        super(CoreCreator, self).__init__()
        self.path = path
        self.setup_ui()
        self.stroke_list = StrokeList(get_letters(path), self.display)

        self.letter_selector.setModel(self.stroke_list.keys_model)

        self.list_view.setModel(self.stroke_list)

        self.letter_selector.currentIndexChanged.connect(self.select_letter)

        self.create_core_btn.clicked.connect(self.create_core)

        self.set_letter_btn.clicked.connect(self.change_letter)

    def change_letter(self):
        new_key = str(self.letter_edt.text())

        indexes = self.list_view.selectedIndexes()

        if new_key and indexes:
            new_key = new_key[0]
            self.stroke_list.change_stroke_key(indexes[0], new_key, self.path)

    def create_core(self):
        segmentation = SEGMENTATION
        letters = self.stroke_list.make_dict(all_letters=True)
        core = make_core(letters, segmentation)
        dump_data = {'segmentation': segmentation}
        dump_data['letters'] = {key: val.tolist()
                                for key, val in core.items() if key != '_'}
        with open(CORE_NAME, 'w') as f:
            json.dump(dump_data, f, indent=1)

    def select_letter(self):
        # set stroke_list key_letter to the one
        # choosen by letter_selector
        new_letter = self.letter_selector.currentText()
        self.stroke_list.set_key_letter(new_letter)

    def setup_ui(self):
        self.resize(800, 480)
        self.grid = QGridLayout(self)

        self.display = pg.PlotWidget(name='st', background='w')

        add_circles(self.display, (1, 2))

        self.grid.addWidget(self.display, 0, 0, 2, 2)

        self.display.getViewBox().setXRange(-np.pi, np.pi)
        self.display.getViewBox().setYRange(-np.pi / 2, np.pi / 2)
        self.display.getViewBox().setAspectLocked()

        self.list_view = QListView(self)
        self.grid.addWidget(self.list_view, 0, 2, 1, 2)

        self.letter_selector = QComboBox(self)
        self.grid.addWidget(self.letter_selector, 1, 2, 1, 2)

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
    cc = CoreCreator('../raw/simple')
    cc.show()
    sys.exit(app.exec_())
