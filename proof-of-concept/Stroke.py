#! /usr/bin/env python

# from PySide.QtGui import QWidget, QApplication, QGridLayout

# import sys

# import threading

# import serial
# from math import sin, cos, radians, atan2, sqrt, asin
import numpy as np

# #from unify_definition import get_letter

# from stroke_widget import StrokeWidget

# from time import clock, time, sleep


class Stroke(object):


    def __init__(self):    
        self.gyro_min = 1000

        self.timer = 0
        self.gyro_time_out = 10

        self.M = np.matrix(np.eye(3))

        self.min_length = 20

        self.data = np.array(())

        self.X_offset=0

        self.X_rad_old = 0
        
        self.X_rad = 0
        self.Y_rad = 0
        
        self.widget = None

        self.on_done = None

        #calculating sroke global size vars
        self.positions_range = None
        self.reset_size()

    def process_size(self, delay, acceleration):
        # if np.linalg.norm(acceleration) < 4:
        #     acceleration = np.array([0, 0, 0])
        self.speed = self.speed + acceleration * delay
        delta_p = self.speed * delay + acceleration * (delay*delay) /2
        self.position = self.position + delta_p
        if self.positions_range is None:
            self.positions_range = np.array([self.position])
        else:
            self.positions_range = np.vstack((self.positions_range, self.position))

    def reset_size(self):     
        self.positions_range = None
        self.position = np.array([0, 0, 0])
        self.speed = np.array([0, 0, 0])

    def set_data_sphere(self,Yr,g):
        self.gyro = g
        if self.gyro > self.gyro_min:

            self.timer = self.gyro_time_out
            
            if self.data.size == 0:
                y = np.array([Yr[0], Yr[1], 0])
                y /= np.linalg.norm(y)

                z = np.array([0., 0., 1.])

                x = np.cross(y,z)
                x /= np.linalg.norm(x)

                self.M = np.matrix(np.vstack((x,y,z)))
                self.reset_size()

            #rotate vector to local system
            Yt = np.array([Yr]).T
            transformed = self.M*Yt
            new_point = np.array([transformed[0, 0],
                                  transformed[1, 0],
                                  transformed[2, 0]])

            if self.data.size == 0:
                self.data = np.array([new_point])
            else:
                self.data = np.vstack((self.data, np.array(new_point) ))

            self.widget.set_coords_stereo(new_point)


        else:
            self.timer -= 1
            if self.timer == 0:
                dimention = 0
                if self.positions_range is not None:
                    data = self.positions_range
                    dimention = np.linalg.norm(np.max(data, axis=0) - np.min(data, axis=0))

                if self.on_done is not None:
  
                    self.on_done({'stroke': self.data, 'dimention': dimention})

                self.data = np.array(())
                self.widget.reset_stroke()
                self.reset_size()
               



    def set_data_radian(self,Yr,g):
        self.gyro = g
        if self.gyro > self.gyro_min:

            self.timer = self.gyro_time_out
            
            if self.data.size == 0:
                self.X_offset = np.arctan2(Yr[0],Yr[1])
                self.reset_size()

            self.X_rad = np.arctan2(Yr[0],Yr[1]) - self.X_offset

            if self.X_rad > self.X_rad_old+np.pi:
                self.X_rad -= 2*np.pi

            if self.X_rad < self.X_rad_old-np.pi:
                self.X_rad += 2*np.pi

            self.X_rad_old = self.X_rad

            try:
                self.Y_rad = np.arcsin(Yr[2])
            except:
                pass

            x_to_write = self.X_rad
            y_to_write = -self.Y_rad

            if self.data.size == 0:
                self.data = np.array([[x_to_write, y_to_write]])
            else:
                self.data = np.vstack((self.data, np.array((x_to_write, y_to_write)) ))

            self.widget.set_coords(x_to_write, y_to_write)


        else:
            self.timer -= 1
            if self.timer == 0:
                if self.on_done is not None:
                    self.on_done(self.data)
                self.data = np.array(())
                self.widget.reset_stroke()
                self.X_offset = 0
                self.reset_size()           

    def set_data(self,Yr,g):
        #self.set_data_radian(Yr, g)
        self.set_data_sphere(Yr,g)
