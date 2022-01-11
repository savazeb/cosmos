import sys
sys.path.append("..")

from api.control.robot import robot
import posix_ipc as ipc
import time

x_power = 0
y_power = 0
turn_power = 0

mq = ipc.MessageQueue('/motorPowerQueue', ipc.O_CREAT)

def main():
    try:
        rc = robot("/serialWriteQueue")
        rc.connect()
        time.sleep(1)
        while True:
            mes = mq.receive()
            power = list(map(int, (mes[0].decode()).split(",")))
            print(power[0], power[1], power[2])
            rc.drive(power[0], power[1], power[2])
            rc.displayPower()
    except KeyboardInterrupt:
        pass
        # irc.disconnect()
main()
