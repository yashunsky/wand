#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


class DumpPipe(object):
    def __init__(self):
        super(DumpPipe, self).__init__()

    def send(self, value):
        pass

    def poll(self):
        return False

    def recv(self):
        return None
