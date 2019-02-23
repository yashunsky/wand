#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
import tkinter as tk


class Sequence(tk.Frame):
    def __init__(self, parent, sprites, side, bg):
        super(Sequence, self).__init__(parent)

        self.configure()

        self.sprites = sprites
        self.side = side

        height = list(sprites.values())[0]['height']

        self.canvas = tk.Canvas(parent, width=1, height=height, bg=bg)
        self.canvas.configure(highlightthickness=0)
        self.canvas.pack(expand=False)

        self.current_sequence = []

    def set(self, sequence):
        if ''.join(self.current_sequence) not in ''.join(sequence):
            self.canvas.delete('all')

        images = [self.sprites[(self.side, position)] for position in sequence]
        width = sum(image['width'] for image in images)

        self.canvas.configure(width=width)

        offset = len(self.current_sequence)

        left = sum(image['width'] for image in images[:offset])
        for image in images[offset:]:
            self.canvas.create_image(left, 0,
                                     image=image['data'],
                                     anchor=tk.NW)
            left += image['width']

        self.current_sequence = copy(sequence)


if __name__ == '__main__':
    from sprites_loader import get_sprites
    window = tk.Tk()

    sprites = get_sprites()

    sequence = Sequence(window, sprites, 'left', '#ebcd89')
    sequence.set(['Ad', 'As', 'Au'])
    sequence.pack()

    tk.mainloop()
