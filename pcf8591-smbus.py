#!/usr/bin/env python

import time
import smbus
import logging

class PCF8591:
    ADDR               = 0x48
    
    REG_IODIR          = 0x00
    REG_IPOL           = 0x01
    REG_IOCON          = 0x05
    REG_GPIO           = 0x09
    
    def __init__(self, subaddress = 0, bus = 0):
        self.bus = smbus.SMBus(bus)
        self.addr = self.ADDR | (subaddress & 0x07)
        return
    
    def setMode(self, outputOn = False, inputMode = 0, autoIncrement = False, channel = 0):
        mode = channel | ((inputMode & 0x03) << 4) 
        if outputOn: mode |= 0x80
        if autoIncrement: mode |= 0x04

	logging.debug("Setting mode %02x" % (mode))
        self.bus.write_byte_data(self.addr, mode, 0)
	self.mode = mode
        return
        
    def readChannel(self, channel):
	mode = (self.mode & 0xFC) | (channel & 0x03)
        #pi.i2c_write_device(self.handle, [mode])
        #self.bus.write_byte(self.addr, mode)
        #(count, data) = pi.i2c_read_device(self.handle, 2)
        data = self.bus.read_word_data(self.addr, mode)
        return data

    def readChannels(self):
	mode = (self.mode & 0xFC)
        self.bus.write_byte_data(self.addr, mode, 0)
        #(count, data) = pi.i2c_read_device(self.handle, 6)
        data = self.bus.read_block_data(self.addr, 6)
        return data[2:]

def test1():
    c = PCF8591(bus=1)
    c.setMode(autoIncrement = True)
    print c.readChannel(0)
    return
    for i in range(25):
        data = c.readChannels()
        logging.debug("Read from ADC: %s" % str(list(data)))
        time.sleep(1)
    return

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test1()
