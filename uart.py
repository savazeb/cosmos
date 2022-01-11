import posix_ipc as ipc
import threading
import serial
import time

direction_q = ipc.MessageQueue('/directionQueue', ipc.O_CREAT)
hit_q = ipc.MessageQueue('/hitQueue', ipc.O_CREAT)
wq = ipc.MessageQueue('/serialWriteQueue', ipc.O_CREAT)

ser = serial.Serial('/dev/ttyTHS1', 115200, timeout=0)

def uart_recv():
    while True:
        line = ser.readline()
        if(line):
            print(int.from_bytes(line, 'little'))
            if (int.from_bytes(line, 'little') & 0xf0):
                print("hitted")
                hit_q.send(line)
            print("direction")
            direction_q.send(line)

def uart_send():
    while True:
        wmes = wq.receive()
        print("".join(("\\x{:02X}".format(c) for c in wmes[0])))
        ser.write(wmes[0])

recv_thread = threading.Thread(target=uart_recv)
send_thread = threading.Thread(target=uart_send)

recv_thread.start()
send_thread.start()

