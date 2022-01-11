import sys
sys.path.append("../..")

from api.control.PID import PID
from api.control.sensor import sensor
from api.control.robot import robot
import posix_ipc as ipc
import time
import threading

graphq = ipc.MessageQueue('/graphQueue', ipc.O_CREAT)
mq = ipc.MessageQueue('/keyQueue', ipc.O_CREAT)
mq.block = False

cam = sensor('cam', '/detectionQueue', False, 2)

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

def getPressed():
    try:
        mes = mq.receive()
        key = list((mes[0].decode()).split(","))
        key = int(key[0]), list(map(int, key[1:3])), list(map(float, key[3:]))
        return key
    except:
        return None

""" GLOBAL VARIABLE HERE """
SENSOR_TYPE = [('cam', 0.04)]
ATTRIBUTE = 'data'

RESCALER = 0.1
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
THRES = 40
WINDOW_CENTER = int(WINDOW_WIDTH / 2) * RESCALER
LEFT_BOUND = int(WINDOW_CENTER - (THRES * RESCALER))
RIGHT_BOUND = int(WINDOW_CENTER + (THRES * RESCALER))

STOP = 0, 0, 0

class power:
    value = 0, 0, 0
    last_value = value
    def set(self, x, y, turn):
        self.last_value = self.value
        self.value = x, y ,turn

def main():
    print(WINDOW_CENTER, LEFT_BOUND, RIGHT_BOUND)
    start = 0
    last_start = start
    min_power = 20
    max_power = 50
    kp = 1
    ki = 0
    kd = 0

    obj_pid = PID(kp, ki, kd, WINDOW_CENTER)
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
                obj_pid.setOutputLimits((-max_power, max_power))
                obj_pid.setKValue(kp, ki ,kd)
                if start != last_start:
                    cx = 0
                    graphq.send(",".join(map(str, [start, cx, WINDOW_CENTER])))
                last_start = start
            if start:
                conf, (cx, _ ) = getattr(cam, ATTRIBUTE)
                print(cam.data)
                # print('[app] conf:', conf)
                if conf:
                    # print('[app] see you')
                    cx *= RESCALER
                    # print('[app] cx:', cx)
                    print('[app] cx:', cx)
                    graphq.send(",".join(map(str, [start, cx, WINDOW_CENTER])))
                    if cx > LEFT_BOUND and cx < RIGHT_BOUND:  
                        print('[app] ready to shoot')
                        pwr.set(*STOP)
                    else:
                        out = -obj_pid.update(cx)
                        if out < min_power and out > 0:
                            out = min_power
                        if out > -min_power and out < 0:
                            out = -min_power
                        print("[app] out: ", out)
                        pwr.set(0, 0, out)
                else:
                    pwr.set(*STOP)
            else:
                pwr.set(*STOP)
            if pwr.value != pwr.last_value:
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