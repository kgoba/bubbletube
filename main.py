#!/usr/bin/env python

import threading
import logging
import random
import time
import sys

import hal
from hal import RGBLeds
from hal import Valves
from hal import Sensors
from hal import Controls
from hal import Status

LOGFILE = None
LOGLEVEL = logging.INFO

def rgbTask(rgb):
    names = ["R", "G", "B"]
    color = [0.1, 0.3, 0.2]
    while True:
        idx = random.randint(0, 2)
        dir = random.randint(0, 1) * 2 - 1
        num = random.randint(100, 250)
        #logging.info("Channel %s %d %.2f %.2f %.2f" % (names[idx], dir, color[0], color[1], color[2]))
        for c in range(num):
            color[idx] += 0.002 * dir
            if color[idx] > 0.5:
                color[idx] = 0.5
                break
            if color[idx] < 0.0:
                color[idx] = 0.0
                break
            rgb.setLED(0, color[0], color[1], color[2])
            rgb.setLED(1, color[0], color[1], color[2])
            rgb.setLED(2, color[0], color[1], color[2])
            time.sleep(0.02)
    return

def main(argv):
    logging.basicConfig(filename=LOGFILE,level=LOGLEVEL)
    logging.info("Starting up")
    hal.init()

    rgb = RGBLeds()
    valves = Valves()
    sensors = Sensors()
    controls = Controls()
    status = Status()

    logging.info("Devices initialized")
    
    t1 = threading.Thread(target = rgbTask, args = (rgb,))
    logging.info("Threads initialized")

    status.set(0)
    t1.start()
    while True:
        states = sensors.read()
        for i in range(6):
            if states[i]:
                status.set(i + 1)
            else:
                status.clear(i + 1)
        time.sleep(0.2)
    return
    
if __name__ == "__main__":
    main(sys.argv)
