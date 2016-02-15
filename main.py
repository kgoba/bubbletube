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

RGB_IDLE_MIN = 0.01
RGB_IDLE_MAX = 0.12
RGB_TOUCH    = 0.30

def rgbTask(rgb, touchEvents):
    names = ["R", "G", "B"]
    color = [0.1, 0.3, 0.2]
    while True:
        idx = random.randint(0, 2)
        dir = random.randint(0, 1) * 2 - 1
        num = random.randint(100, 250)
        #logging.info("Channel %s %d %.2f %.2f %.2f" % (names[idx], dir, color[0], color[1], color[2]))
        for c in range(num):
            color[idx] += 0.001 * dir
            if color[idx] > RGB_IDLE_MAX:
                color[idx] = RGB_IDLE_MAX
                break
            if color[idx] < RGB_IDLE_MIN:
                color[idx] = RGB_IDLE_MIN
                break
            r = color[0]
            g = color[1]
            b = color[2]
            if touchEvents[0].isSet():
                rgb.setLED(0, r + RGB_TOUCH, g + RGB_TOUCH, b + RGB_TOUCH)
            else:
                rgb.setLED(0, r, g, b)
            if touchEvents[1].isSet():
                rgb.setLED(1, r + RGB_TOUCH, g + RGB_TOUCH, b + RGB_TOUCH)
            else:
                rgb.setLED(1, r, g, b)
            if touchEvents[2].isSet():
                rgb.setLED(2, r + RGB_TOUCH, g + RGB_TOUCH, b + RGB_TOUCH)
            else:
                rgb.setLED(2, r, g, b)
            
            time.sleep(0.02)
    return

def valveTask(valves, status, touchEvents):
    while True:
        v1 = touchEvents[0].isSet()
        v2 = touchEvents[1].isSet()
        v3 = touchEvents[2].isSet()
         
        status.setValue(1, v1)
        status.setValue(2, v2)
        status.setValue(3, v3)
        valves.setValve(1, v1)
        valves.setValve(2, v2)
        valves.setValve(3, v3)
        time.sleep(0.1)
    return

def sensorTask(sensors, touchEvents):
    while True:
        states = sensors.read()
        any = False
        for i in range(6):
            if states[i]:
                touchEvents[i].set()
                any = True
        if any:
            time.sleep(1)
        else:
            for i in range(6):
                touchEvents[i].clear()
            time.sleep(0.1)
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
    
    touchEvents = [threading.Event() for i in range(6)]
    t1 = threading.Thread(target = rgbTask, args = (rgb, touchEvents))
    t2 = threading.Thread(target = sensorTask, args = (sensors, touchEvents))
    t3 = threading.Thread(target = valveTask, args = (valves, status, touchEvents))
    logging.info("Threads initialized")

    status.set(0)
    t1.start()
    t2.start()
    t3.start()
    while True:
        time.sleep(1)
        pass
    return
    
if __name__ == "__main__":
    main(sys.argv)
