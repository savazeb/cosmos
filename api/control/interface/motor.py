"""
NOTES - class for motor system
"""
from .ps3.controller import bType, bNumber
from .mapper import bitMapper

MAX_POWER = 100
MIN_POWER = -100

class motor():
    def __init__(self, init_value = 1,x_value = 0, y_value = 0, turn_value = 0):
        # variable for motor power
        self.x_axis_power = x_value
        self.y_axis_power = y_value
        self.turn_power = turn_value
    
    # change power from percentage to signed short
    def power(self, value):
        if value > MAX_POWER or value < MIN_POWER:
            raise ValueError("value must be between -100.0 ~ 100.0")
        return int((value / 100) * (32767 if value >= 0 else  32768))
    
    # set and reset the value
    def set_power(self, x_value, y_value, turn_value):
        self.x_axis_power = self.power(x_value)
        self.y_axis_power = self.power(y_value)
        self.turn_power = self.power(turn_value)
    def reset_power(self):
        self.x_axis_power = 0
        self.y_axis_power = 0
        self.turn_power = 0

    # function for driving purpose
    def move_x(self):
        return bitMapper(self.x_axis_power, 
            bType.LEFTSTICK, bNumber.LEFTSTICK_X)
    def move_y(self):
        return bitMapper(self.y_axis_power,
            bType.LEFTSTICK,bNumber.LEFTSTICK_Y)
    def move_turn(self):
        return bitMapper(self.turn_power,
            bType.RIGHTSTICK, bNumber.RIGHTSTICK_X)
