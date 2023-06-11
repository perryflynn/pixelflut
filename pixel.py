import socket
import threading
import time
import random
from pprint import pprint

"""
Draws a square with androm colorized pixels on a
pixelflut canvas.
Implemented with multi threading, dying thread detection
and respawning of threads
"""

HOST = 'gpn-flut.poeschl.xyz'
PORT = 1234

CANVAS_X = 1650
CANVAS_Y = 400
WIDTH=100
HEIGHT=100

KILL = False

def randcolor():
    r = lambda: random.randint(0, 50)
    g = lambda: random.randint(100, 150)
    b = lambda: random.randint(200,250)

    c = [ r(), g(), b() ]
    random.shuffle(c)

    return '%02X%02X%02X' % (c[0], c[1], c[2])

def buildpixeldata():
    for x in range(CANVAS_X, CANVAS_X+WIDTH):
        for y in range(CANVAS_Y, CANVAS_Y+HEIGHT):
            yield f"PX {x} {y} {randcolor()}"

def threadfunc(id, i):
    global threadsdied
    global threadsdied_sema
    global threadsconnected
    global originaldatalist
    global KILL

    success = False
    oldconnectioncount = -1

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        send = sock.send

        with threadsdied_sema:
            threadsconnected += 1
            success = True

        data = None

        while True:

            if threadsconnected != oldconnectioncount:
                print(f"reslice thread {i}")
                datalist = list(map(lambda x: x[1], filter(lambda y: y[0] % i == 0, enumerate(originaldatalist))))
                random.shuffle(datalist)
                data = bytes("\n".join(datalist), 'ascii')
                oldconnectioncount = threadsconnected

            for _ in range(0, 200):
                send(data)
                time.sleep(0.01)

            if KILL:
                break

    except (socket.timeout, BlockingIOError) as error:
        print(f"Thread {id} died: {error}")

        with threadsdied_sema:
            threadsdied += 1

    if success:
        threadsconnected -= 1

    print(f"Thread {id} ended")

threadcount = 8
threadsstarted = 0
threadsconnected = 0
threadsdied = 0
threadsdied_sema = threading.BoundedSemaphore(value=1)
originaldatalist = list(buildpixeldata())

while not KILL:
    try:
        if threadsstarted - threadsdied < threadcount:
            threadsstarted += 1
            print(f"Start thread {threadsstarted} ({threadsdied} died, {threadsconnected} active)")
            threading.Thread(target=threadfunc, args=(threadsstarted, threadsstarted-threadsdied)).start()
        else:
            print(f"Threads connected: {threadsconnected}")
            time.sleep(1)
    except KeyboardInterrupt:
        KILL = True
