#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk


class CapitalText(tk.Text):
    def __init__(self, parent, bg, fg, font, capital_color):
        super(CapitalText, self).__init__(parent, bd=0, pady=0, padx=0,
                                          highlightthickness=0)
        self.tag_config('start', foreground=capital_color)
        self.configure(bg=bg, fg=fg,
                       width=1, height=1,
                       font=font, state=tk.DISABLED)

    def set_text(self, text):
        lines = text.split('\n')
        self.configure(state=tk.NORMAL,
                       width=max(map(lambda x: len(x), lines)) + 1,
                       height=len(lines))
        self.delete('1.0', tk.END)
        self.insert(tk.END, text)

        for l in range(len(lines)):
            line = l + 1
            self.tag_add('start', '%d.0' % line, '%d.1' % line)

        self.configure(state=tk.DISABLED)
