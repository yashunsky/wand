#!/usr/bin/env python
# -*- coding: utf8 -*-

from input_generator import InputGenerator, TIME_STAMP_RANGE, TIME_SCALE


class StickInputGenerator(InputGenerator):
    def parse_line(self, line):
        try:
            data = [float(value) for value in line.split(';')]
        except ValueError:
            return None

        device_id = 0
        time_stamp = data[0]
        button = data[1] > 0

        delta = (0 if self.prev_timestamp[device_id] is None
                 else time_stamp - self.prev_timestamp[device_id])

        self.prev_timestamp[device_id] = time_stamp

        delta = delta + TIME_STAMP_RANGE if delta < 0 else delta

        data[0] = delta * TIME_SCALE

        return {"button": button,
                "delta": data[0],
                "gyro": self.gyro_remap(data[2:5]),
                "acc": data[5:8]}
