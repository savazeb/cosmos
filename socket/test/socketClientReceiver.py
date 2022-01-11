import posix_ipc as ipc

mq = ipc.MessageQueue('/socketClientReceiveQueue', ipc.O_CREAT)

while True:
        mes, pri = mq.receive()
        print(mes)
