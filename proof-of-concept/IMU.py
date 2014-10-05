#! /usr/bin/env python

# This Module is C-to-Python translation of the following libraries:
# https://github.com/pololu/minimu-9-ahrs-arduino

# Original header:
# MinIMU-9-Arduino-AHRS
# Pololu MinIMU-9 + Arduino AHRS (Attitude and Heading Reference System)
# Copyright (c) 2011 Pololu Corporation.
# http://www.pololu.com/
# MinIMU-9-Arduino-AHRS is based on sf9domahrs by Doug Weibel and Jose Julio:
# http://code.google.com/p/sf9domahrs/
# sf9domahrs is based on ArduIMU v1.5 by Jordi Munoz and William Premerlani, Jose
# Julio and Doug Weibel:
# http://code.google.com/p/ardu-imu/
# MinIMU-9-Arduino-AHRS is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# MinIMU-9-Arduino-AHRS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
# more details.
# You should have received a copy of the GNU Lesser General Public License along
# with MinIMU-9-Arduino-AHRS. If not, see <http://www.gnu.org/licenses/>.

from math import sin, cos, atan2, sqrt, asin, pi

import numpy as np


# These are environment constants.
# Don't mess with them unless you know what you are doing.
GRAVITY = 256
GYRO_GAIN = 0.0012217304763960308  # np.radians(0.07) TODO: Check 0.064
KP_ROLLPITCH = 0.02
KI_ROLLPITCH = 0.00002
KP_YAW = 1.2
KI_YAW = 0.00002
ACCELEROMETER_SCALE = 16
MAGNETS_OFFSET = 0.5

PLATFORM_SPECIFIC_QUOTIENTS = {
    'stm': (744, -499, -491, 1857, 530, 426),
    'arduino': (-504, -615, -564, 597, 488, 384)
}

CALIBRATION_LENGTH = 32  # In cycles


# TODO: Later should be replaced with numpy.array *
def vector_scale(vector, scale):
    return map(lambda a: a * scale, vector)

def vector_add(vector1, vector2):
    return map(sum, zip(vector1, vector2))

def matrix_multiply(a, b, mat):
    op=[0]*3
    for x in xrange(3):
        for y in xrange(3):
            for w in xrange(3):
                op[w]=a[x][w]*b[w][y]
            mat[x][y]=0
            mat[x][y]=op[0]+op[1]+op[2]

class IMU(object):
    def __init__(self, platform):
        self.magnets_min = np.array(PLATFORM_SPECIFIC_QUOTIENTS[platform][:3])
        self.magnets_max = np.array(PLATFORM_SPECIFIC_QUOTIENTS[platform][3:6])

        self.gyroscope_readings_offset = np.zeros(3)
        self.accelerometer_readings_offset = np.zeros(3)

        self.mag_heading = 0

        self.omega_p = np.zeros(3)
        self.omega_i = np.zeros(3)

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.error_roll_pitch = np.zeros(3)
        self.error_yaw = np.zeros(3)

        self.gyro_sat = 0

        self.dcm_matrix = np.eye(3)

        self.counter = 0

        self.in_calibration = True

    def parse_data(self, data):
        delay = data[0]
        accelerometer_readings = np.array(data[1:4]) / ACCELEROMETER_SCALE
        magnetometer_readings = np.array(data[4:7])
        gyroscope_readings = np.array(data[7:10])
        sensors = {'accelerometer': accelerometer_readings,
                   'magnetometer': magnetometer_readings,
                   'gyroscope': gyroscope_readings}
        return delay, sensors

    def calc(self, data):
        delay, sensors = self.parse_data(data)

        if self.in_calibration:
            self.calibration_loop(sensors)
        else:
            self.main_loop(delay, sensors)

    def calibration_loop(self, sensors):
        if self.counter < CALIBRATION_LENGTH:
            self.gyroscope_readings_offset += sensors['gyroscope']
            self.accelerometer_readings_offset += sensors['accelerometer']
            self.counter += 1
        else:
            self.gyroscope_readings_offset /= CALIBRATION_LENGTH
            self.accelerometer_readings_offset /= CALIBRATION_LENGTH

            g_axis = (self.accelerometer_readings_offset /
                np.linalg.norm(self.accelerometer_readings_offset))
            self.accelerometer_readings_offset -= GRAVITY * g_axis

            self.counter = 0
            self.in_calibration = False
            print 'calibration done'


    def main_loop(self, delay, sensors):
        self.counter += 1

        sensors['gyroscope'] = self.offset_gyro(sensors['gyroscope'])
        sensors['accelerometer'] = self.offset_accel(sensors['accelerometer'])
        if self.counter > 5:
            self.counter = 0
            self.compass_heading(sensors['magnetometer'])

        self.matrix_update(sensors, delay)
        self.normalize()
        self.drift_correction(sensors)
        self.Euler_angles()

    def compass_heading(self, magnets):
        cos_roll = cos(self.roll)
        sin_roll = sin(self.roll)
        cos_pitch = cos(self.pitch)
        sin_pitch = sin(self.pitch)

        magnets_norm = ((magnets - self.magnets_min) /
            (self.magnets_max - self.magnets_min) - MAGNETS_OFFSET)

        mag_x = (magnets_norm[0] * cos_pitch + magnets_norm[1] * sin_roll *
                 sin_pitch + magnets_norm[2] * cos_roll * sin_pitch)
        mag_y = (magnets_norm[1] * cos_roll - magnets_norm[2] * sin_roll)

        self.mag_heading = atan2(-mag_y, mag_x)

    def offset_gyro(self, gyro_readings):
        return (gyro_readings - self.gyroscope_readings_offset) * GYRO_GAIN

    def offset_accel(self, accelerometer_readings):
        return self.accelerometer_readings_offset - accelerometer_readings

    def normalize(self):

        error=0
        temporary=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        renorm=0

        error= -np.dot(self.dcm_matrix[0],self.dcm_matrix[1])*.5

        temporary[0] = vector_scale(self.dcm_matrix[1], error)
        temporary[1] = vector_scale(self.dcm_matrix[0], error)

        temporary[0] = vector_add(temporary[0], self.dcm_matrix[0])
        temporary[1] = vector_add(temporary[1], self.dcm_matrix[1])

        temporary[2] = np.cross(temporary[0],temporary[1])

        renorm= .5 *(3 - np.dot(temporary[0],temporary[0]))
        self.dcm_matrix[0] = vector_scale(temporary[0], renorm)

        renorm= .5 *(3 - np.dot(temporary[1],temporary[1]))
        self.dcm_matrix[1] = vector_scale(temporary[1], renorm)

        renorm= .5 *(3 - np.dot(temporary[2],temporary[2]))
        self.dcm_matrix[2] = vector_scale(temporary[2], renorm)

    def drift_correction(self, sensors):
        self.scaled_omega_p = [0]*3
        self.scaled_omega_i = [0]*3

        Accel_magnitude = np.linalg.norm(sensors['accelerometer']) / GRAVITY

        Accel_weight = 1 - 2*abs(1 - Accel_magnitude)

        if Accel_weight < 0:
            Accel_weight = 0
        if Accel_weight > 1:
            Accel_weight = 1

        self.error_roll_pitch = np.cross(sensors['accelerometer'],self.dcm_matrix[2])
        self.omega_p = vector_scale(self.error_roll_pitch,KP_ROLLPITCH*Accel_weight)

        self.scaled_omega_i = vector_scale(self.error_roll_pitch,KI_ROLLPITCH*Accel_weight)
        self.omega_i = vector_add(self.omega_i,self.scaled_omega_i)

        mag_heading_x = cos(self.mag_heading)
        mag_heading_y = sin(self.mag_heading)
        errorCourse=(self.dcm_matrix[0][0]*mag_heading_y) - (self.dcm_matrix[1][0]*mag_heading_x)
        self.error_yaw = vector_scale(self.dcm_matrix[2],errorCourse)

        self.scaled_omega_p = vector_scale(self.error_yaw,KP_YAW)
        self.omega_p = vector_add(self.omega_p,self.scaled_omega_p)

        self.scaled_omega_i = vector_scale(self.error_yaw,KI_YAW)
        self.omega_i = vector_add(self.omega_i,self.scaled_omega_i)

    def matrix_update(self, sensors, delay):
        # adding integrator and proportional term
        omega = sensors['gyroscope'] + self.omega_i + self.omega_p

        (x, y, z) = omega * delay

        update_matrix = np.matrix([[ 1, -z,  y],
                                   [ z,  1, -x],
                                   [-y,  x,  1]])

        # TODO: Fixup this shit
        self.dcm_matrix = np.matrix(self.dcm_matrix)
        self.dcm_matrix *= update_matrix
        self.dcm_matrix = np.array(self.dcm_matrix)

    def Euler_angles(self):
        self.pitch = -asin(self.dcm_matrix[2][0])
        self.roll = atan2(self.dcm_matrix[2][1],self.dcm_matrix[2][2])
        self.yaw = atan2(self.dcm_matrix[1][0],self.dcm_matrix[0][0])

    def get_direction(self):
        return self.dcm_matrix[:, 1]
