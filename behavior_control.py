#!/usr/bin/python
"""
NOTES - Main app for controlling the robot behavior
[ALGORITHM]
 - object tracker ( camera ) --> pid_obj
 - wall follower ( laser sensor ) --> wall_pid
 - direction finder ( IR sensor )
"""

import threading
import time
from api.control.sensor import sensor
from api.control.robot import robot
from api.control.PID import PID
import math
import numpy as np

CAM = 'cam'
IR = 'ir'
LIDAR = 'lidar'

cam = sensor(CAM, '/detectionQueue', False, 2)
ir = sensor(IR, '/directionQueue', False, 3)
lidar = sensor(LIDAR, '/pointQueue')

""" THREAD CLASS """
class sensor_thread(threading.Thread):
    def __init__(self, name, delay, *args, **kwargs):
        super(sensor_thread, self).__init__(*args, **kwargs)
        self._stopper = threading.Event()
        self.name = name
        self.delay = delay
    def stopit(self):
        self._stopper.set()
    def stopped(self):
        return self._stopper.isSet()
    def run(self):
        while True:
            if self.stopped():
                return
            if self.name == 'cam':
                cam.set_data()
            if self.name == 'ir':
                ir.set_data()
            if self.name ==  'lidar':
                lidar.set_data()
            time.sleep(self.delay)

""" FUNCTION """
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

""" GLOBAL VARIABLE HERE """
# static variable
SENSOR_TYPE = [('cam', 0.04), ('ir', 0.15),  ('lidar', 0.0)]

# static variable for object detection
RESCALER = 0.1
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_THRES = 40
WINDOW_CENTER = int(WINDOW_WIDTH / 2) * RESCALER
WINDOW_LEFT_BOUND = int(WINDOW_CENTER - (WINDOW_THRES * RESCALER))
WINDOW_RIGHT_BOUND = int(WINDOW_CENTER + (WINDOW_THRES * RESCALER))

# static variable for wall follower
DELTA_ANGLE = 50
RIGHT_HAND_ANGLE = 90
HELPER_HAND_ANGLE = RIGHT_HAND_ANGLE + DELTA_ANGLE
FACE_ANGLE = 180
WALL_THRES = 1
WALL_DISTANCE = 60
WALL_LEFT_BOUND = WALL_DISTANCE - WALL_THRES
WALL_RIGHT_BOUND = WALL_DISTANCE + WALL_THRES

# static variable for controlling motor speed
# main power class
class power:
    value = 0, 0, 0
    last_value = value
    def set(self, x, y, turn):
        self.last_value = self.value
        self.value = x, y ,turn
        
AVOIDER_POWER = 35
STOP = 0, 0, 0
MAX_POWER = 70
MIN_POWER = 5
TURN_POWER = 40
POWER_LIMITS = (-MAX_POWER, MAX_POWER)

""" PID PARAM SET HERE """
# for object detection
KP_OBJ = 0.57
KI_OBJ = 0
KD_OBJ = 0.14

# for wall follower
KP_WALL = 0.53
KI_WALL = 0
KD_WALL = 0.1

# init class
rc = robot('/serialWriteQueue')
time.sleep(5)
rc.connect()
time.sleep(0.5)
pid_obj = PID(KP_OBJ, KI_OBJ, KD_OBJ, WINDOW_CENTER)
pid_obj.setOutputLimits(POWER_LIMITS)
pid_wall = PID(KP_WALL, KI_WALL, KD_WALL, WALL_DISTANCE)
pid_wall.setOutputLimits(POWER_LIMITS)
pwr = power()

""" MAIN FUNTION BEGINS HERE """
class behavior_control():
    workers = []
    start_time = None
    def __init__(self):
        if not self.workers:
            for name, delay in SENSOR_TYPE:
                print('[info] start thread : ' , name)
                thread = sensor_thread(name, delay)
                self.workers.append(thread)
                thread.start()
        self.reset()
    def start(self):
        if not self.initted:
            pid_wall.clear()
            pid_obj.clear()
            self.initted = True
        self.behavior()
    def end(self):
        self.reset()
    def reset(self):
        self.initted = None
        self.start_time = None
        rc.stop()
    def behavior(self):
        self.start_time = self.start_time if self.start_time else time.time()
        # map all data received from sensor
        conf, (cx, _ ) = cam.data
        direction = ir.data
        point = lidar.data
        if conf:
            self.start_time = time.time()
            pid_wall.clear()
            cx *= RESCALER
            print('[bc] cx:', cx)
            if cx > WINDOW_LEFT_BOUND and cx < WINDOW_RIGHT_BOUND:  
                print('[bc] ready to shoot')
                rc.shoot()
                pwr.set(*STOP)
            else:
                out = -pid_obj.update(cx)
                if out < MIN_POWER and out > 0:
                    out = MIN_POWER
                if out > -MIN_POWER and out < 0:
                    out = -MIN_POWER
                print("[bc] out: ", out)
                pwr.set(0, 0, out)
        
        elif direction:
            print('[app] behavior control', direction)
            if 'left' in direction:
                self.start_time = time.time()
                pwr.set(0, 0, -TURN_POWER)
            if 'right' in direction or direction == 'back':
                self.start_time = time.time()
                pwr.set(0, 0, TURN_POWER)

        # checking if error occured before processing
        elif (time.time() - self.start_time) > 4:
            if type(point) is np.ndarray:
                print("waller")
                pid_obj.clear()
                angles, ranges = point
                right_hand = float(ranges[find_nearest(angles, RIGHT_HAND_ANGLE)])
                helper_hand = float(ranges[find_nearest(angles, HELPER_HAND_ANGLE)])
                face = float(ranges[find_nearest(angles, FACE_ANGLE)])
                teta = math.radians(DELTA_ANGLE)
                if face < 50 and face > 0:
                    pwr.set(0, 0, AVOIDER_POWER)
                elif right_hand > 0 and helper_hand > 0:
                    alpha = math.atan((right_hand * math.cos(teta) - helper_hand)/ (right_hand * math.sin(teta)))
                    rx_distance = helper_hand * math.cos(math.radians(alpha))
                    if rx_distance > WALL_RIGHT_BOUND or rx_distance < WALL_LEFT_BOUND:
                        out = pid_wall.update(rx_distance)
                        if out < MIN_POWER and out > 0:
                            out = MIN_POWER
                        if out > -MIN_POWER and out < 0:
                            out = -MIN_POWER
                        print('[bc]', rx_distance, out)
                        pwr.set(0, MAX_POWER, out)
                    else:
                        pwr.set(0, MAX_POWER, 0)
                else:
                    pwr.set(*STOP)
            else:
                pwr.set(*STOP) 
        else:   
            pwr.set(*STOP)
        # drive the motor when new value is setted
        print('[bc] power:', pwr.value)
        if pwr.value != pwr.last_value:
            rc.drive(*pwr.value)
        time.sleep(0.001)
