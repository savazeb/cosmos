import json
import numpy as np

class stride():
    def __init__(self, size = 1):
        self.size = size
        self.list = self.init_list()
    def init_list(self):
        return []
    def add(self, value):
        self.list.append(value)
        if len(self.list) > self.size:
            self.list = self.list[1:self.size+1]

directions = [
    "not found",    # 0b0000
    "left",         # 0b0001
    "left back",    # 0b0010
    "left back",    # 0b0011
    "right back",   # 0b0100
    "undefined",    # 0b0101
    "back",         # 0b0110
    "left back",    # 0b0111
    "right",        # 0b1000
    "undefined",    # 0b1001
    "undefined",    # 0b1010
    "undefined",    # 0b1011
    "right back",   # 0b1100
    "undefined",    # 0b1101
    "right back",   # 0b1110
    "undefined",    # 0b1111
    None
]

def most_frequent(List):
    return max(set(List), key = List.count)

ir_s = stride()
def getDirection(ir, stride_length):
    ir_s.size = stride_length
    direction = int.from_bytes(ir[0], 'little') & 0xf if ir else 16
    ir_s.add(direction)
    print(ir_s.list)
    #print("[api] dir list", ir_s.list)
    return directions[most_frequent(ir_s.list)]


def find(List):
    if sum(x is not None for x in List) >= int(len(List)/2):
        return max(index for index, item in enumerate(List) if item)
    return max(index for index, item in enumerate(List) if not item)

cam_s = stride()
OBJ_BUFF = None, [None,None]
def getDetectedObject(cam, stride_length):
    cam_s.size = stride_length
    if cam:
        obj = json.loads(cam[0].decode())
        cam_s.add(list((obj["confidence"], obj["center"])))
    else:
        cam_s.add(list(OBJ_BUFF))
    # print('[api] obj list', cam_s.list)
    return cam_s.list[find(cam_s.list)]

def getPoint(lidar):
    angles = []
    ranges = []
    if lidar:
        point = lidar[0].decode()
        point = json.loads(point)
        for key, val in point.items():
            angles.append(int(key))
            ranges.append(float(val))
        return np.array([angles, ranges])


