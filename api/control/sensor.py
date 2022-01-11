
import posix_ipc as ipc
from .getitem import getDirection, getPoint, getDetectedObject  

class sensor():
    def __init__(self, sensor_type, qname, block = True, stride_length = 1):
        self.sensor_type = sensor_type
        # create sensor queue
        self.queue = ipc.MessageQueue(qname, ipc.O_CREAT)
        self.queue.block = block
        # error checking stride length
        self.stride_length = stride_length
        # init sensor data
        self.data = self.reset_data()
    def cleanup(self):
        self.queue.close()
        self.queue.unlink()
    def read_message(self):
        return self.queue.receive()
    def set_data(self):
        try:
            msg = self.read_message()
        except:
            msg = None
        if self.sensor_type == 'ir':
            self.data = getDirection(msg, self.stride_length)
        if self.sensor_type == 'cam':
            self.data = getDetectedObject(msg, self.stride_length)
        if self.sensor_type == 'lidar':
            self.data = getPoint(msg)
    def reset_data(self):
        return None
