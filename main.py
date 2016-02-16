#!/usr/bin/env python

import threading
import logging
import random
import time
import sys

from config import *

import hal
from hal import *

def blinkTask(status):
    while True:
        status.set(7)
        time.sleep(0.1)
        status.clear(7)
        time.sleep(0.9)
    return

def clip(x, low, high):
    if x < low: return low
    if x > high: return high
    return x

def rgbTask(rgb, index, events):
    names = ["R", "G", "B"]
    color = [0.1, 0.1, 0.1]
    while True:
        idx = random.randint(0, 2)
        dir = random.randint(0, 1) * 2 - 1
        num = random.randint(100, 300)
        logging.debug("LED %d.%s %d %.2f %.2f %.2f" % (index, names[idx], dir, color[0], color[1], color[2]))
        for c in range(num):
            r = color[0]
            g = color[1]
            b = color[2]
            any = False
            for e in events:
                if e.isSet():
                    any = True
                    break
            if any:
                r = r * RGB_TOUCH_MUL + RGB_TOUCH_ADD
                g = g * RGB_TOUCH_MUL + RGB_TOUCH_ADD
                b = b * RGB_TOUCH_MUL + RGB_TOUCH_ADD
            
            rgb.setLED(index, clip(r, 0, RGB_MAX), clip(g, 0, RGB_MAX), clip(b, 0, RGB_MAX))
            
            color[idx] += RGB_SPEED * dir
            if color[idx] > RGB_IDLE_MAX:
                color[idx] = RGB_IDLE_MAX
                break
            if color[idx] < RGB_IDLE_MIN:
                color[idx] = RGB_IDLE_MIN
                break
            time.sleep(0.040)
    return

class TimeKeeper:
    def __init__(self, controls):
        self.controls = controls
        self.update()

    def delayOn(self):
        time.sleep(self.t_on)

    def delayOff(self, valve):
        time.sleep(self.t_off[valve])

    def update(self):
        cval = self.controls.read()
        self.t_on = T_ON_MIN + (T_ON_MAX - T_ON_MIN) * cval[0]
        self.t_off = [0] * 3
        for i in range(3):
            self.t_off[i] = T_OFF_MIN + (T_OFF_MAX - T_OFF_MIN) * cval[i + 1]
        return

def valveSimpleTask(valves, controls, status, index, c_idx, touchEvent, delay = 0): 
    while True:
        while not touchEvent.wait():
            pass
        status.set(index + 1)
        if delay:
            time.sleep(delay)
        while touchEvent.isSet():
            logging.debug("Valve %d ON" % index)
            valves.enable(index)
            controls.delayOn()
            logging.debug("Valve %d OFF" % index)
            valves.disable(index)
            controls.delayOff(c_idx)
        status.clear(index + 1)
    return

def sensorTask(sensors, status, touchEvents):
    while True:
        states = sensors.read()
        any = False
        for i in range(6):
            if states[i]:
                touchEvents[i].set()
                any = True
            else:
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
    timer = TimeKeeper(controls)

    logging.info("Devices initialized")

    seq = ( (1, 1, 1, 0), 
            (2, 2, 2, 0),
            (3, 3, 3, 0),
            (4, 1, 1, 0), (4, 2, 1, 0.6), (4, 3, 1, 1.2),
            (5, 1, 1, 1.0), (5, 2, 1, 0.5), (5, 3, 1, 0),
            (6, 1, 1, 0.5), (6, 2, 1, 0), (6, 3, 1, 0.5)
    )

    touchEvents = [threading.Event() for i in range(6)]
    tasks = []
    tasks.append( threading.Thread(target = blinkTask, args = (status, )) )
    for (t_idx, v_idx, c_idx, delay) in seq:
        tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, v_idx - 1, c_idx, touchEvents[t_idx - 1], delay)) )
         
    for i in range(3):
        events = [touchEvents[i], touchEvents[3], touchEvents[4], touchEvents[5]]
        tasks.append( threading.Thread(target = rgbTask, args = (rgb, i, events)) )
    tasks.append( threading.Thread(target = sensorTask, args = (sensors, status, touchEvents)) )

    logging.info("Threads initialized")

    status.set(0)
    for task in tasks:
        task.start()
    
    logging.info("Threads started")

    while True:
        time.sleep(1)
        timer.update()
    
    return
    
if __name__ == "__main__":
    main(sys.argv)
