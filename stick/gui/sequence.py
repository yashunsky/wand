#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from copy import copy
import tkinter as tk


class Sequence(tk.Frame):
    def __init__(self, parent, sprites, side, bg):
        super(Sequence, self).__init__(parent)

        self.configure(bg=bg)

        self.sprites = sprites
        self.side = side

        height = list(sprites.values())[0]['height']

        self.canvas = tk.Canvas(parent, width=1, height=height, bg=bg)
        self.canvas.configure(highlightthickness=0)
        self.canvas.pack(expand=False)

        self.current_sequence = []

        self.reset_hint()

    def reset_hint(self):
        self.hint = []
        self.hint_str = ''
        self.hint_ids = []

    def set_hint(self, hint):
        images = [self.sprites[(self.side + '_shaded', position)]
                  for position in hint]
        width = sum(image['width'] for image in images)
        self.canvas.configure(width=width)
        self.hint = hint
        self.hint_ids = self.place_images(images)
        self.hint_str = ''.join(hint)

    def remove_hint(self):
        for id in self.hint_ids:
            self.canvas.delete(id)
        self.reset_hint()

    def set(self, sequence):
        current_str = ''.join(self.current_sequence)
        new_str = ''.join(sequence)

        if current_str not in new_str:
            self.canvas.delete('all')
            self.reset_hint()

        if new_str not in self.hint_str:
            self.remove_hint()

        images = [self.sprites[(self.side, position)] for position in sequence]

        if not self.hint:
            width = sum(image['width'] for image in images)
            self.canvas.configure(width=width)

        offset = len(self.current_sequence)

        self.place_images(images, offset)

        self.current_sequence = copy(sequence)

    def place_images(self, images, offset=0):
        image_ids = []
        left = sum(image['width'] for image in images[:offset])
        for image in images[offset:]:
            image_id = self.canvas.create_image(left, 0,
                                                image=image['data'],
                                                anchor=tk.NW)
            image_ids.append(image_id)
            left += image['width']
        return image_ids


if __name__ == '__main__':
    from sprites_loader import get_sprites
    window = tk.Tk()

    sprites = get_sprites()

    sequence = Sequence(window, sprites, 'left', '#ebcd89')
    sequence.set_hint(['Ad', 'As', 'Au', 'Hs', 'Hd'])
    sequence.set(['Ad', 'As', 'Au'])
    sequence.pack()

    tk.mainloop()
