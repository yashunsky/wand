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
GYRO_GAIN = 0.0012217304763960308  # np.radians(0.07)
KP_ROLLPITCH = 0.02
KI_ROLLPITCH = 0.00002
KP_YAW = 1.2
KI_YAW = 0.00002

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
            mat[x][y]=0;
            mat[x][y]=op[0]+op[1]+op[2]

class IMU(object):
    def __init__(self, platform):
        self.data_source = []

        (self.min_mx, self.min_my,
         self.min_mz, self.max_mx,
         self.max_my, self.max_mz) = PLATFORM_SPECIFIC_QUOTIENTS[platform]

        self.delay = 0.02
        self.an = [0]*6
        self.an_offset = [0]*6

        (self.ax, self.ay, self.az,
         self.mx, self.my, self.mz,
         self.gx, self.gy, self.gz,
         self.cmx, self.cmy, self.cmz,) = [0]*12

        self.mag_heading = 0

        self.accel_vector = [0]*3
        self.gyro_vector = [0]*3
        self.omega_vector = [0]*3
        self.omega_p = [0]*3
        self.omega_i = [0]*3
        self.omega = [0]*3

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.error_roll_pitch = [0]*3
        self.error_yaw = [0]*3

        self.gyro_sat = 0

        self.dcm_matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self.update_matrix = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
        self.temporary_matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        self.counter = 0

        self.in_calibration = True

    def calc(self, data):
        delay, self.data_source = data[0], data[1:]
        if self.in_calibration:
            self.calibration_loop()
        else:
            self.main_loop(delay)

    def calibration_loop(self):
        if self.counter < CALIBRATION_LENGTH:
            self.read_gyro()
            self.read_accel()
            for y in xrange(6):
                self.an_offset[y] += self.an[y]
            self.counter += 1
        else:
            for y in xrange(6):
                self.an_offset[y] = self.an_offset[y]/CALIBRATION_LENGTH

            g_vector = np.array(self.an_offset[3:6])

            g_axis = g_vector / np.linalg.norm(g_vector)

            g_vector -= GRAVITY * g_axis

            self.an_offset[3] = g_vector[0]
            self.an_offset[4] = g_vector[1]
            self.an_offset[5] = g_vector[2]

            self.counter = 0

            self.in_calibration = False
            print 'calibratoion done'


    def main_loop(self, delay):
            self.counter += 1
            self.delay = delay

            #print self.delay

            self.read_gyro()
            self.read_accel()
            if self.counter > 5:
                self.counter = 0
                self.read_compass()
                self.compass_heading()

            self.matrix_update()
            self.normalize()
            self.drift_correction()
            self.Euler_angles()

    def compass_heading(self):
        cos_roll = cos(self.roll)
        sin_roll = sin(self.roll)
        cos_pitch = cos(self.pitch)
        sin_pitch = sin(self.pitch)

        self.cmx = (self.mx - self.min_mx) / (self.max_mx - self.min_mx) - 0.5
        self.cmy = (self.my - self.min_my) / (self.max_my - self.min_my) - 0.5
        self.cmz = (self.mz - self.min_mz) / (self.max_mz - self.min_mz) - 0.5

        mag_x = self.cmx*cos_pitch+self.cmy*sin_roll*sin_pitch+self.cmz*cos_roll*sin_pitch
        mag_y = self.cmy*cos_roll-self.cmz*sin_roll

        self.mag_heading = atan2(-mag_y,mag_x)

    def read_gyro(self):
        self.an[0] = self.data_source[6]
        self.an[1] = self.data_source[7]
        self.an[2] = self.data_source[8]

        self.gx = (self.an[0] - self.an_offset[0])
        self.gy = (self.an[1] - self.an_offset[1])
        self.gz = (self.an[2] - self.an_offset[2])

    def read_accel(self):
        self.an[3] = self.data_source[0] / 16
        self.an[4] = self.data_source[1] / 16
        self.an[5] = self.data_source[2] / 16

        self.ax = self.an_offset[3] - self.an[3]
        self.ay = self.an_offset[4] - self.an[4]
        self.az = self.an_offset[5] - self.an[5]

    def read_compass(self):
        self.mx = self.data_source[3]
        self.my = self.data_source[4]
        self.mz = self.data_source[5]

    def normalize(self):

        error=0;
        temporary=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        renorm=0;

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
        self.dcm_matrix[2] = vector_scale(temporary[2], renorm);

    def drift_correction(self):

        self.scaled_omega_p = [0]*3
        self.scaled_omega_i = [0]*3;

        Accel_magnitude = sqrt(self.accel_vector[0]*self.accel_vector[0] +
                               self.accel_vector[1]*self.accel_vector[1] +
                               self.accel_vector[2]*self.accel_vector[2])

        Accel_magnitude = Accel_magnitude / GRAVITY

        Accel_weight = 1 - 2*abs(1 - Accel_magnitude)

        if Accel_weight < 0:
            Accel_weight = 0
        if Accel_weight > 1:
            Accel_weight = 1

        self.error_roll_pitch = np.cross(self.accel_vector,self.dcm_matrix[2])
        self.omega_p = vector_scale(self.error_roll_pitch,KP_ROLLPITCH*Accel_weight);

        self.scaled_omega_i = vector_scale(self.error_roll_pitch,KI_ROLLPITCH*Accel_weight);
        self.omega_i = vector_add(self.omega_i,self.scaled_omega_i);

        mag_heading_x = cos(self.mag_heading);
        mag_heading_y = sin(self.mag_heading);
        errorCourse=(self.dcm_matrix[0][0]*mag_heading_y) - (self.dcm_matrix[1][0]*mag_heading_x)
        self.error_yaw = vector_scale(self.dcm_matrix[2],errorCourse)

        self.scaled_omega_p = vector_scale(self.error_yaw,KP_YAW)
        self.omega_p = vector_add(self.omega_p,self.scaled_omega_p)

        self.scaled_omega_i = vector_scale(self.error_yaw,KI_YAW)
        self.omega_i = vector_add(self.omega_i,self.scaled_omega_i)

    def matrix_update(self):

        self.gyro_vector[0]=self.gx * GYRO_GAIN #gyro x roll
        self.gyro_vector[1]=self.gy * GYRO_GAIN #gyro y pitch
        self.gyro_vector[2]=self.gz * GYRO_GAIN #gyro Z yaw

        self.accel_vector[0]=self.ax
        self.accel_vector[1]=self.ay
        self.accel_vector[2]=self.az

        self.omega = vector_add(self.gyro_vector, self.omega_i) #adding proportional term
        self.omega_vector = vector_add(self.omega, self.omega_p) # //adding Integrator term

        self.update_matrix[0][0]=0
        self.update_matrix[0][1]=-self.delay*self.omega_vector[2]#;//-z
        self.update_matrix[0][2]=self.delay*self.omega_vector[1]#;//y
        self.update_matrix[1][0]=self.delay*self.omega_vector[2]#;//z
        self.update_matrix[1][1]=0
        self.update_matrix[1][2]=-self.delay*self.omega_vector[0]#;//-x
        self.update_matrix[2][0]=-self.delay*self.omega_vector[1]#;//-y
        self.update_matrix[2][1]=self.delay*self.omega_vector[0]#;//x
        self.update_matrix[2][2]=0

        matrix_multiply(self.dcm_matrix,self.update_matrix,self.temporary_matrix)#; //a*b=c

        for x in xrange(3):
            for y in xrange(3):
                self.dcm_matrix[x][y]+=self.temporary_matrix[x][y]

    def Euler_angles(self):

        self.pitch = -asin(self.dcm_matrix[2][0])
        self.roll = atan2(self.dcm_matrix[2][1],self.dcm_matrix[2][2])
        self.yaw = atan2(self.dcm_matrix[1][0],self.dcm_matrix[0][0])
