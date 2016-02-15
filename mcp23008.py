#!/usr/bin/env python

import time
import smbus
import logging

class MCP23008:
    ADDR               = 0x20
    
    REG_IODIR          = 0x00
    REG_IPOL           = 0x01
    REG_IOCON          = 0x05
    REG_GPIO           = 0x09
    
    def __init__(self, subaddress = 0, bus = 0):
        self.bus = smbus.SMBus(bus)
        self.addr = self.ADDR | (subaddress & 0x07)
        return
    
    def setDirection(self, direction):
        """ Set GPIO port (8 pins) direction (0 - OUTPUT, 1 - INPUT) """
        self.bus.write_byte_data(self.addr, self.REG_IODIR, direction)
        return
        
    def setPins(self, value):
        """ Set GPIO port value (for output pins) """
        self.bus.write_byte_data(self.addr, self.REG_GPIO, value)
        return

def test1():
    c = MCP23008(bus=1)
    c.setDirection(0x00)
        
    for i in range(30):
        logging.debug("LEDs on")
        c.setPins(0xFF)
        time.sleep(0.25)
        logging.debug("LEDs off")
        c.setPins(0x00)
        time.sleep(0.25)
    return

if __name__ == "__main__":
    test1()
