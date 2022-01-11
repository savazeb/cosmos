from behavior_control import behavior_control
import posix_ipc as ipc
import threading
import time

hq = ipc.MessageQueue('/hitQueue', ipc.O_CREAT) #from uart.py
sq = ipc.MessageQueue('/socketClientSendQueue', ipc.O_CREAT)
rq = ipc.MessageQueue('/socketClientReceiveQueue', ipc.O_CREAT)

HITTED = 'hit'

game_msg = None

def hit_status():
    print('[info] start thread : ' , "hit")
    while True:
        if hq.current_messages:
            sq.send(HITTED)

def game_status():
    global game_msg
    print('[info] start thread : ' , "game")
    while True:
        msg = rq.receive()
        print(msg[0].decode())
        game_msg = msg[0].decode()

behavior = behavior_control()
time.sleep(3)

class game_control():
    init = None
    def __init__(self):
        hitted_thread = threading.Thread(target=hit_status)
        hitted_thread.start()
        game_thread = threading.Thread(target=game_status)
        game_thread.start()
    def __setted__(self):
        if game_msg == "game start":
            return True
        if game_msg == "game set":
            return None
    def start(self):
        if self.__setted__():
            behavior.start()
        else:
            behavior.end()


        