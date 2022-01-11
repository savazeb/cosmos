"""
NOTES - ps3 button values
JOYAXISMOTION
event.axis              event.value
0 - x axis left thumb   (+1 is right, -1 is left)
1 - y axis left thumb   (+1 is down, -1 is up)
2 - x axis right thumb  (+1 is right, -1 is left)
3 - y axis right thumb  (+1 is down, -1 is up)
4 - right trigger
5 - left trigger
JOYBUTTONDOWN | JOYBUTTONUP
event.button
START = 3
"""

class bType():
    LEFTSTICK = 2
    RIGHTSTICK = 2
    START = 3 # shouta custom
    R1 = 1
class bNumber():
    LEFTSTICK_X = 0
    LEFTSTICK_Y = 1
    RIGHTSTICK_X = 2
    RIGHTSTICK_Y = 3 #ignored by stm
    START = 9
    R1 = 11
