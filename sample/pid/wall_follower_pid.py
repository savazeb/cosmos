import sys
sys.path.append("../..")

from api.control.PID import PID
from api.control.sensor import sensor
from api.control.robot import robot
import posix_ipc as ipc
import time
import threading
import math
import numpy as np

graphq = ipc.MessageQueue('/graphQueue', ipc.O_CREAT)
mq = ipc.MessageQueue('/keyQueue', ipc.O_CREAT)
mq.block = False

lidar = sensor('lidar', '/pointQueue')

""" THREAD CLASS """
class sensor_thread(threading.Thread):
    def __init__(self, name, delay,*args, **kwargs):
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

def getPressed():
    try:
        mes = mq.receive()
        key = list((mes[0].decode()).split(","))
        key = int(key[0]), list(map(int, key[1:3])), list(map(float, key[3:]))
        return key
    except:
        return None

""" GLOBAL VARIABLE HERE """
SENSOR_TYPE = [('lidar', 0.0)]
ATTRIBUTE = 'data'

DELTA_ANGLE = 50
RIGHT_HAND_ANGLE = 90
HELPER_HAND_ANGLE = RIGHT_HAND_ANGLE + DELTA_ANGLE
FACE_ANGLE = 180

WALL_THRES = 1
WALL_DISTANCE = 60
WALL_LEFT_BOUND = WALL_DISTANCE - WALL_THRES
WALL_RIGHT_BOUND = WALL_DISTANCE + WALL_THRES

AVOIDER_POWER = 35
STOP = 0, 0, 0

class power:
    value = 0, 0, 0
    def set(self, x, y, turn):
        self.value = x, y ,turn

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def main():
    start = 0
    last_start = start
    min_power = 20
    max_power = 50
    kp = 1
    ki = 0
    kd = 0

    lidar_pid = PID(kp, ki, kd, WALL_DISTANCE)
    workers = []
    for name, delay in SENSOR_TYPE:
        print('[info] start thread : ' , name)
        thread = sensor_thread(name, delay)
        workers.append(thread)
        thread.start()
    try:
        rc = robot('/serialWriteQueue')
        time.sleep(5)
        rc.connect()
        time.sleep(0.5)
        pwr = power()
        while True:
            key = getPressed()
            if key:
                print(key)
                start, (min_power, max_power), (kp, ki, kd) = key
                lidar_pid.setOutputLimits((-max_power, max_power))
                lidar_pid.setKValue(kp, ki ,kd)
                if start != last_start:
                    rx_distance = 0
                    graphq.send(",".join(map(str, [start, rx_distance, WALL_DISTANCE])))
                last_start = start
            if start:
                point = lidar.data
                print(type(point))
                if type(point) is np.ndarray:
                    print("ye")
                    angles, ranges = point
                    right_hand = float(ranges[find_nearest(angles, RIGHT_HAND_ANGLE)])
                    helper_hand = float(ranges[find_nearest(angles, HELPER_HAND_ANGLE)])
                    face = float(ranges[find_nearest(angles, FACE_ANGLE)])
                    teta = math.radians(DELTA_ANGLE)
                    if face < 50:
                        print("50")
                        pwr.set(0, 0, AVOIDER_POWER)
                    elif right_hand > 0 and helper_hand > 0:
                        print("ye")
                        alpha = math.atan((right_hand * math.cos(teta) - helper_hand)/ (right_hand * math.sin(teta)))
                        rx_distance = helper_hand * math.cos(math.radians(alpha))
                        graphq.send(",".join(map(str, [start, rx_distance, WALL_DISTANCE])))
                        if rx_distance > WALL_RIGHT_BOUND or rx_distance < WALL_LEFT_BOUND:
                            out = lidar_pid.update(rx_distance)
                            if out < min_power and out > 0:
                                out = min_power
                            if out > -min_power and out < 0:
                                out = -min_power
                            print(rx_distance, out)
                            pwr.set(0, max_power, out)
                        else:
                            pwr.set(0, max_power, 0)
                    else:
                        pwr.set(*STOP) 
                else:
                    pwr.set(*STOP)
            else:
                pwr.set(*STOP)
            rc.drive(*pwr.value)
            time.sleep(0.001)
    except KeyboardInterrupt:
        print('[info] interrupt pressed')
    print('[main] work finished')
    for worker in workers:
        worker.stopit()
        time.sleep(3)
        worker.join()
    #lidar.cleanup()
    #ir.cleanup()
    #cam.cleanup()
    #rc.disconnect()
    print('[main] end')

main()
