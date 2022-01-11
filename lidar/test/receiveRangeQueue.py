import posix_ipc as ipc
import time
import struct
import numpy as np
import json

point_q = ipc.MessageQueue("/pointQueue", ipc.O_CREAT)


while True:
    angles = []
    ranges = []
    msg = point_q.receive()
    data = msg[0].decode('utf-8')
    data = json.loads(data)
    # print(type(data))
    # print(data)
    # print(len(data))
    for key in data:
        angles.append(int(key))
        ranges.append(float(data[key]))
        # print("{} : {}".format(key, data[key]))
    angles = np.array(angles)
    ranges = np.array(ranges)
    print("angles", angles)
    # print("ranges", type(ranges))