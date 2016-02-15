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

def rgbTask(rgb, index, touchEvent, seqEvent = None):
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
            if touchEvent.isSet():
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

class SeqOn:
    def __init__(self, valves, status, index):
        self.index = index
        self.valves = valves
        self.status = status

    def run(self, cval):
        logging.info("SeqOn %d" % self.index)
        self.valves.enable(self.index)
        self.status.set(self.index)
        t_on = 0.05 + 0.2 * cval[0]
        time.sleep(t_on)

class SeqOff:
    def __init__(self, valves, status, index):
        self.index = index
        self.valves = valves
        self.status = status

    def run(self, cval):
        logging.info("SeqOff %d" % self.index)
        self.valves.disable(self.index)
        self.status.clear(self.index)
        t_off = 0.5 + 2 * cval[1]
        time.sleep(t_off)

class SeqDelay:
    def __init__(self, time):
        self.time = time

    def run(self, cval):
        logging.info("SeqDelay %.2f" % self.time)
        time.sleep(self.time)

def valveTask(valves, controls, status, sequence, touchEvent):
    while True:
        while not touchEvent.wait():
            pass
        cval = controls.read()
        for s in sequence:
            s.run(cval)
        
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
   
    seq1 = [SeqOn(valves, status, 1), SeqOff(valves, status, 1)]
    seq2 = [SeqOn(valves, status, 2), SeqOff(valves, status, 2)]
    seq3 = [SeqOn(valves, status, 3), SeqOff(valves, status, 3)]

    seqlist = [(0, seq1), (1, seq2), (2, seq3), 
               (3, seq1), (3, seq2), (3, seq3)]

    touchEvents = [threading.Event() for i in range(6)]
    tasks = []
    for i in range(3):
        tasks.append( threading.Thread(target = rgbTask, args = (rgb, i, touchEvents[i])) )
    tasks.append( threading.Thread(target = sensorTask, args = (sensors, status, touchEvents)) )
    for (t_idx, seq) in seqlist:
        tasks.append( threading.Thread(target = valveTask, 
            args = (valves, controls, status, seq, touchEvents[t_idx])) )

    logging.info("Threads initialized")

    status.set(0)
    for task in tasks:
        task.start()
    
    while True:
        time.sleep(1)
        pass
    return
    
if __name__ == "__main__":
    main(sys.argv)
