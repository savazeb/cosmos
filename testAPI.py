from api.control import robot
import time
import threading
# for test purpose

rc = robot("/serialWriteQueue")
rc.connect()
time.sleep(2)

def drive():
    while True:
        rc.drive(0 ,0,-100)
        time.sleep(1)
        rc.stop()
        time.sleep(1)
def shoot():
    while True:
        rc.shoot()
        time.sleep(0.5)

try:
    # creating threads
    drive_thread = threading.Thread(target=drive)
    shoot_thread = threading.Thread(target=shoot)
    # starting threads
    drive_thread.start()
    shoot_thread.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # close the api
    rc.disconnect()
    # wait until all threads finish
    drive_thread.join()
    shoot_thread.join()
