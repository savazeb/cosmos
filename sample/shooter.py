import threading
import sys
import time

a = 0
b = 0

def lidar():
    global a
    while True:
        a += 1
        time.sleep(0.25)
def ir():
    global b
    while True:
        b += 1
        time.sleep(0.5)
        
# creating threads
sensor1 = threading.Thread(target=lidar)
sensor2 = threading.Thread(target=ir)
# starting threads
sensor1.daemon=True
sensor2.daemon=True

sensor1.start()
sensor2.start()
try:
    print(a, b)
    time.sleep(1)
except KeyboardInterrupt:
    time.sleep(2)
    # wait until all threads finish
    sys.exit()
sensor1.join()
sensor2.join()
