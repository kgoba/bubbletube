#!/usr/bin/env python

import logging
import random
import time
import sys

import pca9685
import pcf8591
import mcp23008

#import pigpio
import RPi.GPIO as GPIO

LOGFILE = None
LOGLEVEL = logging.INFO

I2CBUS = 1
ADC_SUBADDR = 0
LED_SUBADDR = 0

class RGBLeds:    
    LED_PINS = ((2, 1, 0), (7, 6, 5), (10, 9, 8))
    
    def __init__(self):
        self.driver = pca9685.PCA9685(subaddress = 0, bus = I2CBUS)
        self.driver.setPrescaler(13)
        self.reset()
    
    def setLED(self, index, red = 0, green = 0, blue = 0):
        assert index >= 0 and index < 3
        assert red >= 0.0 and red <= 1.0
        assert green >= 0.0 and green <= 1.0
        assert blue >= 0.0 and blue <= 1.0
        self.driver.setLED(self.LED_PINS[index][0], red)
        self.driver.setLED(self.LED_PINS[index][1], green, delay = 0)
        self.driver.setLED(self.LED_PINS[index][2], blue, delay = 0)
        
    def reset(self):
        self.driver.setAllLED(0)

class Valves:
    GATE_PINS = (17, 27, 22)
    
    def __init__(self):
        for gpio in self.GATE_PINS:
            GPIO.setup(gpio, GPIO.OUT, initial=GPIO.LOW)
        self.reset()
        return

    def enable(self, index):
        self.setValve(index, True)

    def disable(self, index):
        self.setValve(index, False)

    def setValve(self, index, value):
        assert index >= 1 and index <= 3
        assert value == True or value == False
        if value: state = GPIO.HIGH
        else: state = GPIO.LOW

        GPIO.output(self.GATE_PINS[index - 1], state)
        return
        
    def reset(self):
        self.disable(1)
        self.disable(2)
        self.disable(3)
        return


class Sensors:
    CAP_GPIO = (5, 6, 13, 19, 26, 21)
    
    def __init__(self):
        #self.pi = pigpio.pi()
        for gpio in self.CAP_GPIO:
	    GPIO.setup(gpio, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return

    def read(self):
        result = []
        for gpio in self.CAP_GPIO:
            result.append(GPIO.input(gpio))
        return result

class Controls:
    CHANNELS = (3, 2, 1, 0)

    def __init__(self, subaddress = ADC_SUBADDR):
        self.driver = pcf8591.PCF8591(bus = I2CBUS)
        return
        
    def read(self):
        data = self.driver.readChannels()
        if len(data) != 4:
            return None
        return [data[self.CHANNELS[0]], data[self.CHANNELS[1]], 
                data[self.CHANNELS[2]], data[self.CHANNELS[3]]]


class Status:
    LED_GPIO = (7, 6, 5, 4, 3, 2, 1, 0)
    
    def __init__(self, subaddress = LED_SUBADDR):
        self.driver = mcp23008.MCP23008(bus = I2CBUS)
        self.driver.setDirection(0x00)
        self.state = 0
        self.setAll(self.state)
        return
    
    def setAll(self, value):
        self.driver.setPins(value)
        return
    
    def set(self, index):
        self.state |= (1 << self.LED_GPIO[index])
        self.setAll(self.state)
        return
 
    def clear(self, index):
        self.state &= ~(1 << self.LED_GPIO[index])
        self.setAll(self.state)
        return

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
    GPIO.setmode(GPIO.BCM)

    testRGB()
    return
    
if __name__ == "__main__":
    main(sys.argv)
