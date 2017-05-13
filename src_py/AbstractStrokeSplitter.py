#! /usr/bin/env python

import numpy as np


class AbstractStrokeSplitter(object):

    def __init__(self, gyro_min, gyro_timeout, min_length):
        self.gyro_min = gyro_min
        self.gyro_time_out = gyro_timeout
        self.min_length = min_length

        self.timer = 0

        self.is_moving = False

        self.M = np.matrix(np.eye(3))

        self.data = np.array(())

        # calculating sroke global size vars
        self.reset_size()

    def reset_size(self):
        self.positions_range = None
        self.position = np.array([0, 0, 0])
        self.speed = np.array([0, 0, 0])

    def process_size(self, delay, acceleration):
        self.speed = self.speed + acceleration * delay
        delta_p = self.speed * delay + acceleration * (delay * delay) / 2
        self.position = self.position + delta_p
        if self.positions_range is None:
            self.positions_range = np.array([self.position])
        else:
            self.positions_range = np.vstack((self.positions_range,
                                              self.position))

    def set_data(self, heading, gyro):
        self.gyro = gyro

        stroke = None
        dimention = None
        too_short = None

        if self.gyro > self.gyro_min:
            self.on_gyro(True)
            self.is_moving = True
            self.timer = self.gyro_time_out

            if self.data.size == 0:
                y = np.array([heading[0], heading[1], 0])
                if np.linalg.norm(y) != 0:
                    y /= np.linalg.norm(y)
                else:
                    return

                z = np.array([0., 0., 1.])

                x = np.cross(y, z)
                x /= np.linalg.norm(x)

                self.M = np.matrix(np.vstack((x, y, z)))
                self.reset_size()

            # rotate vector to local system
            heading = np.array([heading]).T
            transformed = self.M * heading
            new_point = np.array([transformed[0, 0],
                                  transformed[1, 0],
                                  transformed[2, 0]])

            if self.data.size == 0:
                self.data = new_point
            else:
                self.data = np.vstack((self.data, new_point))
        else:
            self.timer -= 1
            if self.timer == 0:
                self.timer = 0
                dimention = 0
                if self.positions_range is not None:
                    data = self.positions_range
                    dimention = np.linalg.norm(np.max(data, axis=0) -
                                               np.min(data, axis=0))

                if self.data.size / 3 > self.min_length:
                    stroke = self.data  # self.data[:-self.gyro_time_out, :]
                    too_short = False
                    self.on_stroke_done(self.data, dimention)
                else:
                    self.on_gyro(False)
                    too_short = True

            elif self.timer < 0:
                self.timer = -1
                self.is_moving = False

                self.data = np.array(())

        return {'is_moving': self.is_moving,
                'stroke': stroke,
                'dimention': dimention,
                'too_short': too_short}

    def on_stroke_done(self, data, dimention):
        pass

    def on_gyro(self, is_moving):
        pass
