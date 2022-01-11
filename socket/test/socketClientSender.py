import posix_ipc as ipc
import time

mq = ipc.MessageQueue('/socketClientSendQueue', ipc.O_CREAT)

for i in range(100):
    msg = input(">> ")
    mq.send(msg)
