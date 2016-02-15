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
RGB_TOUCH_ADD = 0.14
RGB_TOUCH_MUL = 3.00

def rgbTask(rgb, index, events):
    names = ["R", "G", "B"]
    color = [0.1, 0.1, 0.1]
    while True:
        idx = random.randint(0, 2)
        dir = random.randint(0, 1) * 2 - 1
        num = random.randint(100, 300)
        #logging.info("Channel %s %d %.2f %.2f %.2f" % (names[idx], dir, color[0], color[1], color[2]))
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
                rgb.setLED(index, r * RGB_TOUCH_MUL + RGB_TOUCH_ADD, g * RGB_TOUCH_MUL + RGB_TOUCH_ADD, b * RGB_TOUCH_MUL + RGB_TOUCH_ADD)
            else:
                rgb.setLED(index, r, g, b)
            
            color[idx] += 0.001 * dir
            if color[idx] > RGB_IDLE_MAX:
                color[idx] = RGB_IDLE_MAX
                break
            if color[idx] < RGB_IDLE_MIN:
                color[idx] = RGB_IDLE_MIN
                break
            time.sleep(0.02)
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
        self.t_on = 0.05 + 0.2 * cval[0]
        self.t_off = [0] * 3
        for i in range(3):
            self.t_off[i] = 0.5 + 3.5 * cval[i + 1]
        return

def valveSimpleTask(valves, controls, status, index, touchEvent, delay = 0): 
    while True:
        while not touchEvent.wait():
            pass
        if delay:
            time.sleep(delay)
        while touchEvent.isSet():
            valves.enable(index)
            controls.delayOn()
            valves.disable(index)
            controls.delayOff(index)

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

    seq = ( (1, 1, 0), 
            (2, 2, 0),
            (3, 3, 0),
            (4, 1, 0), (4, 2, 0.6), (4, 3, 1.2),
            (5, 1, 1.0), (5, 2, 0.5), (5, 3, 0),
            (6, 1, 0.5), (6, 2, 0), (6, 3, 0.5)
    )


    touchEvents = [threading.Event() for i in range(6)]
    tasks = []
    for (t_idx, v_idx, delay) in seq:
        tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, v_idx - 1, touchEvents[t_idx - 1], delay)) )
         
    for i in range(3):
        events = [touchEvents[i], touchEvents[3], touchEvents[4], touchEvents[5]]
        tasks.append( threading.Thread(target = rgbTask, args = (rgb, i, events)) )
    tasks.append( threading.Thread(target = sensorTask, args = (sensors, status, touchEvents)) )
    #for (t_idx, seq) in seqlist:
    #    tasks.append( threading.Thread(target = valveTask, 
    #        args = (valves, controls, status, seq, touchEvents[t_idx])) )
    #for i in range(3):
    #    tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, i, touchEvents[i])) )
    #for i in range(3):
    #    tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, i, touchEvents[3], i * 0.6)) )
    #for i in range(3):
    #    tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, i, touchEvents[4], (2 - i) * 0.6)) )
    #delays = [0, 0.6, 0]
    #for i in range(3):
    #    tasks.append( threading.Thread(target = valveSimpleTask, args = (valves, timer, status, i, touchEvents[5], delays[i])) )




    logging.info("Threads initialized")

    status.set(0)
    for task in tasks:
        task.start()
    
    while True:
        time.sleep(1)
        timer.update()
    
    return
    
if __name__ == "__main__":
    main(sys.argv)
