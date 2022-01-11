"""
NOTES - class for sensor system
"""

from .ps3.controller import bType, bNumber
from .mapper import bitMapper

class sensor():
    def __init__(self, light_value = 0):
        self.light = light_value
    def toogle_light(self):
        return bitMapper( int(not self.light), 
            bType.R1, bNumber.R1)