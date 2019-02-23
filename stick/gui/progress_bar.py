#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk


class ProgressBar(tk.Text):
    def __init__(self, parent, bg, fg, font, color, max_value):
        super(ProgressBar, self).__init__(parent, bd=0, pady=0, padx=0,
                                          highlightthickness=0)

        self.tag_config('colored', foreground=color)
        self.insert(tk.END, '•' * max_value)
        self.configure(bg=bg, fg=fg,
                       width=max_value - 4, height=1,  # bad hack :(
                       font=font, state=tk.DISABLED)

    def set_value(self, value):
        self.configure(state=tk.NORMAL)
        self.tag_remove('colored', '1.0', tk.END)
        self.tag_add('colored', '1.0', '1.%d' % value)
        self.configure(state=tk.DISABLED)
