import time
import socket
import threading
import posix_ipc as ipc
import sys

ADDR = "192.168.11.2"
PORT = 20220

rq = ipc.MessageQueue('/socketClientReceiveQueue', ipc.O_CREAT)
sq = ipc.MessageQueue('/socketClientSendQueue', ipc.O_CREAT)

def recv(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data == b'':
                break
            rq.send(data)
            print(data)
        except:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            break
    print("close recv")
    sys.exit()
def send(sock):
    while True:
        try:
            if sq.current_messages:
                data, pri = sq.receive()
                sock.send(data)
        except:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            break
    print("close send")
    sys.exit()
sock = socket.socket(socket.AF_INET)
sock.connect((ADDR, PORT))

pSend = threading.Thread(target=send, args=(sock, ))
pRecv = threading.Thread(target=recv, args=(sock, ))

pSend.start()
pRecv.start()

pSend.join()
pRecv.join()
