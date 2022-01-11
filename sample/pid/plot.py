import posix_ipc as ipc
import threading
import matplotlib
matplotlib.use('GTK3Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import math
import time
import numpy as np

graphq = ipc.MessageQueue('/graphQueue', ipc.O_CREAT)

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

out_value = []
start = 0

def getValue():
    global out_value, start
    status = 0
    while True:
        msg = graphq.receive()
        print(msg)
        start , val, target = list(map(float, (msg[0].decode()).split(","))) 
        if status:     
            out_value.append([val, target])
        status = 1
        if not start:
            out_value = []
            status = 0



thread = threading.Thread(target=getValue)
thread.start()

def main(i):
    print(type(out_value))
    if start:
        ax1.clear()
        ax1.plot(out_value)

ani = animation.FuncAnimation(fig, main, interval=100)
plt.show()

#def main():
#while True:
#        print(out_value)
#        time.sleep(1)

#main()

thread.join()
