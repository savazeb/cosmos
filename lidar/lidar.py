import os
import ydlidar
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
import math
import json
import posix_ipc
import sys

ports = ydlidar.lidarPortList();
port = "/dev/ydlidar";
for key, value in ports.items():
    port = value;
    
laser = ydlidar.CYdLidar();
laser.setlidaropt(ydlidar.LidarPropSerialPort, port);
laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)
laser.setlidaropt(ydlidar.LidarPropLidarType, ydlidar.TYPE_TOF);
laser.setlidaropt(ydlidar.LidarPropDeviceType, ydlidar.YDLIDAR_TYPE_SERIAL);
laser.setlidaropt(ydlidar.LidarPropScanFrequency, 10.0);
laser.setlidaropt(ydlidar.LidarPropSampleRate, 20);
laser.setlidaropt(ydlidar.LidarPropSingleChannel, False);
laser.setlidaropt(ydlidar.LidarPropMaxAngle, 180.0);
laser.setlidaropt(ydlidar.LidarPropMinAngle, -180.0);
laser.setlidaropt(ydlidar.LidarPropMaxRange, 32.0);
laser.setlidaropt(ydlidar.LidarPropMinRange, 0.01);
scan = ydlidar.LaserScan()

point_q = posix_ipc.MessageQueue("/pointQueue", posix_ipc.O_CREAT)

def main():
    global flag
    r = laser.doProcessSimple(scan);
    if r:
        angles = []
        ranges = []
        last_degree = 0
        for point in scan.points:
            degree = math.degrees(point.angle)
            if degree < 0:
                degree = 360 + degree
            degree = int(degree)
            if degree != last_degree:
                angles.append(degree)
                ranges.append(round(point.range * 100 , 2))
            last_degree = degree
        msg = {angles[i] : ranges[i] for i in range(len(angles))}
        # print(sys.getsizeof(msg))
        point_q.send(json.dumps(msg, sort_keys=True, indent=2))

ret = laser.initialize();
if ret:
    ret = laser.turnOn();
    if ret:
        while True:
            main()
    laser.turnOff();
laser.disconnecting();
