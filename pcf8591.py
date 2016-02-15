#!/usr/bin/env python

import time
#import smbus
import logging
import pigpio

pi = pigpio.pi()

class PCF8591:
    ADDR               = 0x48
    
    REG_IODIR          = 0x00
    REG_IPOL           = 0x01
    REG_IOCON          = 0x05
    REG_GPIO           = 0x09
    
    def __init__(self, subaddress = 0, bus = 0):
        #self.bus = smbus.SMBus(0)
        self.bus = bus
        self.addr = self.ADDR | (subaddress & 0x07)
        self.handle = pi.i2c_open(self.bus, self.addr)
        self.setMode(autoIncrement = True)
        return
    
    def setMode(self, outputOn = False, inputMode = 0, autoIncrement = False, channel = 0):
        mode = channel | ((inputMode & 0x03) << 4) 
        if outputOn: mode |= 0x80
        if autoIncrement: mode |= 0x04

	logging.debug("Setting mode %02x" % (mode))
        pi.i2c_write_device(self.handle, [mode])
	self.mode = mode
        return
        
    def readChannel(self, channel):
	#mode = (self.mode & 0xFC) | (channel & 0x03)
        #pi.i2c_write_device(self.handle, [mode])
        (count, data) = pi.i2c_read_device(self.handle, 2)
        return data[1:]

    def readChannels(self):
	mode = (self.mode & 0xFC)
        pi.i2c_write_device(self.handle, [mode])
        (count, data) = pi.i2c_read_device(self.handle, 6)
        return data[2:]

def test1():
    c = PCF8591(bus=1)
    c.setMode(autoIncrement = True)
        
    for i in range(25):
        data = c.readChannels()
        logging.debug("Read from ADC: %s" % str(list(data)))
        time.sleep(1)
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test1()
