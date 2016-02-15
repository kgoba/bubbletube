#!/usr/bin/env python

import logging
import random
import time
import sys

import hal
from hal import *

LOGFILE = None
LOGLEVEL = logging.INFO

def testSensors():
    sensors = Sensors()
    status = Status()
    last = None
    for i in range(100):
        while True:
            now = sensors.read()
            if now != last: break
        print now
        last = now
    return

def testValves():
    valves = Valves()
    for i in range(10):
        valves.enable(1)
        time.sleep(1)
        valves.disable(1)
        time.sleep(1)
    return

def testRGB():
    rgb = RGBLeds()

    logging.debug("Setting RGB LEDs")
    names = ["red", "green", "blue"]

    color = [0.1, 0.3, 0.2]
    while True:
    #for iter in range(100):
        idx = random.randint(0, 2)
        dir = random.randint(0, 1) * 2 - 1
        num = random.randint(30, 200)
        for c in range(num):
            #logging.debug("Setting channel %s" % names[c])
            color[idx] += 0.005 * dir
            if color[idx] > 0.5: color[idx] = 0.5
            if color[idx] < 0.0: color[idx] = 0.0
            rgb.setLED(0, color[0], color[1], color[2])
            rgb.setLED(1, color[0], color[1], color[2])
            rgb.setLED(2, color[0], color[1], color[2])
            time.sleep(0.02)

    #rgb.reset()
    return

def testControls():
    controls = Controls()
    status = Status()
    on = False
    idx = 0
    while True:
        cval = controls.read()
        #logging.debug("Read %s from controls" % str(cval))
        if on:
            status.set(idx)
        else:
            status.clear(idx)
        time.sleep(cval[0] / 400.0 + 0.02)
        #time.sleep(0.05)
        idx += 1
        if idx >= 8:
            on = not on
            idx = 0
    
    #sval = sensors.read()
    #logging.debug("Read %s from sensors" % str(sval))

    return

def main(argv):
    logging.basicConfig(filename=LOGFILE,level=LOGLEVEL)
    logging.info("Starting up")
    hal.init()

    testRGB()
    return
    
if __name__ == "__main__":
    main(sys.argv)
