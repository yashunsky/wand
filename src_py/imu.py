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
# sf9domahrs is based on ArduIMU v1.5 by Jordi Munoz and
# William Premerlani, Jose
# Julio and Doug Weibel:
# http://code.google.com/p/ardu-imu/
# MinIMU-9-Arduino-AHRS is free software: you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
# MinIMU-9-Arduino-AHRS is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with MinIMU-9-Arduino-AHRS. If not, see <http://www.gnu.org/licenses/>.

import numpy as np


# These are environment constants.
# Don't mess with them unless you know what you are doing.
GRAVITY = 256
G = 9.81
GYRO_GAIN = 0.0012217304763960308  # np.radians(0.07) TODO: Check 0.064
KP_ROLLPITCH = 0.02
KI_ROLLPITCH = 0.00002
KP_YAW = 1.2
KI_YAW = 0.00002
ACCELEROMETER_SCALE = 16
MAGNETS_OFFSET = 0.5

CALIBRATION_LENGTH = 32  # In cycles

ACCELEROMETER_DIVIATION = 2
GYROSCOPE_DIVIATION = 16


class IMU(object):
    def __init__(self, magnet_boundaries):
        self.magnet_boundaries = map(np.array, magnet_boundaries)

        self.gyroscope_readings_offset = np.zeros(3)
        self.accelerometer_readings_offset = np.zeros(3)

        self.mag_heading = 0

        self.omega_p = np.zeros(3)
        self.omega_i = np.zeros(3)

        self.angles = {'roll': 0, 'pitch': 0, 'yaw': 0}

        self.dcm_matrix = np.matrix(np.eye(3))

        self.in_calibration = True

        self.acceleration = np.array([0, 0, GRAVITY])
        self.gyro = np.array([0, 0, 0])

        self.a_stack = np.array([0, 0, 0])
        self.g_stack = np.array([0, 0, 0])

    def parse_data(self, data):
        delay = data['delta']

        accelerometer_readings = np.array(data['acc']) / ACCELEROMETER_SCALE
        magnetometer_readings = np.array(data['mag'])
        gyroscope_readings = np.array(data['gyro'])

        sensors = {'accelerometer': accelerometer_readings,
                   'magnetometer': magnetometer_readings,
                   'gyroscope': gyroscope_readings}
        return delay, sensors

    def calc(self, data, axis='z'):
        headings = {'x': self.get_x_direction,
                    'y': self.get_y_direction,
                    'z': self.get_z_direction}

        delay, sensors = self.parse_data(data)

        if self.in_calibration:
            self.recalibration(sensors)
        else:
            self.main_loop(delay, sensors)

        return {'in_calibration': self.in_calibration,
                'accel': self.get_global_acceleration(),
                'gyro': self.gyro / GYRO_GAIN,
                'heading': headings[axis]()}

    def recalibration(self, sensors):
        '''Recalibrate the device if it wasn't significatly moving
        within last CALIBRATION_LENGTH cycles'''

        self.a_stack = np.vstack((self.a_stack,
                                  sensors['accelerometer']))[-CALIBRATION_LENGTH:]

        self.g_stack = np.vstack((self.g_stack,
                                  sensors['gyroscope']))[-CALIBRATION_LENGTH:]

        if len(self.a_stack) < CALIBRATION_LENGTH:
            return
        if len(self.g_stack) < CALIBRATION_LENGTH:
            return

        a_diviation = np.max(np.std(self.a_stack, axis=0))
        g_diviation = np.max(np.std(self.g_stack, axis=0))

        if a_diviation > ACCELEROMETER_DIVIATION:
            return
        if g_diviation > GYROSCOPE_DIVIATION:
            return

        self.gyroscope_readings_offset = np.mean(self.g_stack, axis=0)
        self.accelerometer_readings_offset = np.mean(self.a_stack, axis=0)

        g_axis = (self.accelerometer_readings_offset /
                  np.linalg.norm(self.accelerometer_readings_offset))
        self.accelerometer_readings_offset -= GRAVITY * g_axis

        print self.gyroscope_readings_offset
        print self.accelerometer_readings_offset

        self.a_stack = np.array([0, 0, 0])
        self.g_stack = np.array([0, 0, 0])

        self.in_calibration = False

    def main_loop(self, delay, sensors):
        sensors = self.offset_sensors(sensors)

        # acceleration shoud be accecible from outside
        self.acceleration = sensors['accelerometer']
        self.gyro = sensors['gyroscope']

        self.mag_heading = self.compass_heading(
            sensors['magnetometer'], self.angles, self.magnet_boundaries)

        self.dcm_matrix = self.matrix_update(
            self.dcm_matrix, sensors['gyroscope'], delay,
            self.omega_p, self.omega_i)
        self.dcm_matrix = self.normalize(self.dcm_matrix)
        accel_weight = self.calculate_accel_weight(sensors['accelerometer'])
        error_yaw, error_roll_pitch = self.calculate_error(
            sensors['accelerometer'], self.dcm_matrix, self.mag_heading)
        self.omega_p, self.omega_i = self.drift_correction(
            accel_weight, error_yaw, error_roll_pitch, self.omega_i)
        self.angles = self.euler_angles(self.dcm_matrix)

    def offset_sensors(self, sensors):
        sensors['gyroscope'] = self.offset_gyro(
            sensors['gyroscope'], self.gyroscope_readings_offset)

        sensors['accelerometer'] = self.offset_accel(
            sensors['accelerometer'], self.accelerometer_readings_offset)

        return sensors

    def compass_heading(self, magnets, angles, magnets_boundaries):
        cos_roll = np.cos(angles['roll'])
        sin_roll = np.sin(angles['roll'])
        cos_pitch = np.cos(angles['pitch'])
        sin_pitch = np.sin(angles['pitch'])
        magnets_min = magnets_boundaries[0]
        magnets_max = magnets_boundaries[1]

        magnets_norm = ((magnets - magnets_min) /
                        (magnets_max - magnets_min) - MAGNETS_OFFSET)

        mag_x = (magnets_norm[0] * cos_pitch + magnets_norm[1] * sin_roll *
                 sin_pitch + magnets_norm[2] * cos_roll * sin_pitch)
        mag_y = (magnets_norm[1] * cos_roll - magnets_norm[2] * sin_roll)

        return np.arctan2(-mag_y, mag_x)

    def offset_gyro(self, gyro_readings, gyro_readings_offset):
        return (gyro_readings - gyro_readings_offset) * GYRO_GAIN

    def offset_accel(self, accel_readings, accel_readings_offset):
        return accel_readings - accel_readings_offset

    def renorm(self, array):
        renorm = 0.5 * (3 - np.dot(array, array))
        return array * renorm

    def normalize(self, dcm_matrix):
        temporary = np.matrix(np.zeros((3, 3)))
        error = -np.dot(dcm_matrix[0, :].A1, dcm_matrix[1, :].A1) * 0.5

        temporary[0, :] = dcm_matrix[1, :] * error + dcm_matrix[0, :]
        temporary[1, :] = dcm_matrix[0, :] * error + dcm_matrix[1, :]
        temporary[2, :] = np.cross(temporary[0, :], temporary[1, :])

        # It's quite strange: the commented code should do exactly
        # the same thing, as the uncommented, and it does pass the tests,
        # but only with a much bigger EPSILON.
        # I don't understand, how in could be so:)

        # renorm_coeff = (np.array([3, 3, 3]) -
        #                 np.power(np.linalg.norm(temporary, axis=1),2)) * 0.5

        # renorm_matrix = np.vstack((renorm_coeff,
        #                            renorm_coeff,
        #                            renorm_coeff))

        # return np.matrix(np.multiply(renorm_matrix, temporary))

        return np.matrix([self.renorm(temp.A1) for temp in temporary])

    def calculate_accel_weight(self, acceleration):
        accel_magnitude = np.linalg.norm(acceleration) / GRAVITY

        accel_weight = 1 - 2 * abs(1 - accel_magnitude)

        if accel_weight < 0:
            accel_weight = 0
        if accel_weight > 1:
            accel_weight = 1

        return accel_weight

    def calculate_error(self, acceleration, dcm_matrix, mag_heading):
        mag_heading_x = np.cos(mag_heading)
        mag_heading_y = np.sin(mag_heading)
        error_course = ((dcm_matrix[0, 0] * mag_heading_y) -
                        (dcm_matrix[1, 0] * mag_heading_x))
        error_yaw = dcm_matrix[2, :] * error_course
        error_roll_pitch = np.cross(acceleration, dcm_matrix[2, :].A1)

        return error_yaw.A1, error_roll_pitch

    def drift_correction(self, accel_weight, error_yaw, error_roll_pitch,
                         original_omega_i):
        scaled_omega_p = error_yaw * KP_YAW
        omega_p = (error_roll_pitch * KP_ROLLPITCH * accel_weight +
                   scaled_omega_p)

        scaled_omega_i = error_yaw * KI_YAW
        omega_i = (original_omega_i +
                   error_roll_pitch * KI_ROLLPITCH * accel_weight +
                   scaled_omega_i)

        return omega_p, omega_i

    def matrix_update(self, dcm_matrix, angular_vel, delay, omega_p, omega_i):
        # adding integrator and proportional term
        omega = angular_vel + omega_i + omega_p

        (x, y, z) = omega * delay

        update_matrix = np.matrix([[1, -z, y],
                                   [z, 1, -x],
                                   [-y, x, 1]])

        return np.matrix(dcm_matrix) * update_matrix

    def euler_angles(self, dcm_matrix):
        pitch = -np.arcsin(dcm_matrix[2, 0])
        roll = np.arctan2(dcm_matrix[2, 1], dcm_matrix[2, 2])
        yaw = np.arctan2(dcm_matrix[1, 0], dcm_matrix[0, 0])
        return {'pitch': pitch, 'roll': roll, 'yaw': yaw}

    def get_x_direction(self):
        return self.dcm_matrix[:, 0].A1

    def get_y_direction(self):
        return self.dcm_matrix[:, 1].A1

    def get_z_direction(self):
        return self.dcm_matrix[:, 2].A1

    def get_global_acceleration(self):
        local_a = np.matrix([self.acceleration])
        global_a = (local_a * self.dcm_matrix.T).A1 / GRAVITY
        global_a = global_a - np.array([0, 0, 1])
        global_a = global_a * G

        return global_a
