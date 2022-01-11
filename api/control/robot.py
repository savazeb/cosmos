#!/usr/bin/python
"""
NOTES - class for robot system
please CONNECT beforewards & DISCONNECT afterwards!
"""
from .interface.motor import motor
from .interface.sensor import sensor
from .interface.ps3.controller import bType, bNumber
from .interface.mapper import bitMapper

import posix_ipc
import time
import struct
import logging

logging.basicConfig(format='%(asctime)s | %(levelname)s: %(message)s', level=logging.NOTSET)

# Main class for controlling the robot
class robot(motor, sensor):
    def __init__(self, queue_name = "/robotControlQueue", start_value = 1):
        # init the parent class
        motor.__init__(self)
        sensor.__init__(self)
        # setup the queue for message
        self.__mq = posix_ipc.MessageQueue(queue_name, posix_ipc.O_CREAT )
        self.start  = start_value
    def reset(self):
        self.__mq.close()
        self.__mq.unlink()
        self.start = int(not(self.start))
    def send_msg(self, value):
        self.__mq.send(value)
        time.sleep(0.05)
    # attribute for controlling the motor
    def displayPower(self):
        logging.info('motor speed\n \t\t\tx\t: {}\n \t\t\ty\t: {}\n \t\t\tturn\t: {}'.format(self.x_axis_power, self.y_axis_power * -1 - ( 1 if self.y_axis_power != 0 else 0), self.turn_power))
    def connect(self):
        self.send_msg(bitMapper(self.start, bType.START, bNumber.START))
        logging.info('motor connected! ready to use!')
    def disconnect(self):
        self.reset()
        logging.info('motor disconnected! Thank you! :)')
    def drive(self, x_power, y_power, turn_power):
        motor.set_power(self, x_power, y_power, turn_power)
        self.send_msg(motor.move_x(self))
        self.send_msg(motor.move_y(self))
        self.send_msg(motor.move_turn(self))
    def stop(self):
        motor.reset_power(self)
        self.send_msg(motor.move_x(self))
        self.send_msg(motor.move_y(self))
        self.send_msg(motor.move_turn(self))
    def drive_time(self, x_power, y_power, turn_power, delay):
        self.drive(x_power, y_power, turn_power)
        time.sleep(delay)
        self.stop()
    # attribute for controlling the sensor
    def shoot(self):
        self.send_msg(sensor.toogle_light(self))
