import sys
sys.path.append("..")

from api.control.robot import robot
import posix_ipc as ipc
import time


def main():
    rc = robot("/serialWriteQueue")
    rc.connect()
    time.sleep(1)
    while True:
        rc.shoot()
        time.sleep(1)

main()
