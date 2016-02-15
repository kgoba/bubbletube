#!/usr/bin/env python

import time
import smbus
import logging

class PCA9685:
    ADDR0              = 0x40
    
    REG_MODE1          = 0x00
    REG_MODE2          = 0x01
    REG_LED0_ON_L      = 0x06
    REG_ALL_LED_ON_L   = 0xFA
    REG_PRESCALE       = 0xFE

    def __init__(self, subaddress = 0, bus = 0):
        self.bus = smbus.SMBus(bus)
        self.addr0 = self.ADDR0 | (subaddress & 0x0F)
        self.reset()
        self.setMode1(ai = True, sleep = False)
        return

    def setPrescaler(self, value):
        self.setMode1(ai = True, sleep = True)
        cmd = self.REG_PRESCALE
        self.bus.write_byte_data(self.addr0, cmd, value)
        self.setMode1(ai = True, sleep = False)
        return

    def reset(self):
        self.bus.write_byte_data(self.addr0, self.REG_MODE1, 0)
        return

    def setLED(self, index, duty = 0.0, delay = 0.0):
        if index and (index < 0 or index > 15): 
            raise Exception("LED index out of bounds")
            
        on = (int(delay * 4096)) & 0x0FFF
        off = (on + int(duty * 4095)) & 0x0FFF
            
        data = [on & 0xFF, (on >> 8) & 0xFF, off & 0xFF, (off >> 8) & 0xFF]
        if index != None:
            cmd = self.REG_LED0_ON_L + 4 * index
        else:
            cmd = self.REG_ALL_LED_ON_L
        #self.setMode1(ai = True, sleep = True)
        #logging.debug("Setting ON=%d OFF=%d (idx %s reg %d) %s" % (on, off, str(index), cmd, str(data)))    
        self.bus.write_i2c_block_data(self.addr0, cmd, data)
        #self.setMode1(ai = True, sleep = False)
        return

    def setAllLED(self, duty = 0, delay = 0):
        self.setLED(None, duty, delay)
        return
        
    def setMode1(self, restart = False, extclk = False, ai = False, sleep = True, 
                        sub1 = False, sub2 = False, sub3 = False, allcall = True):
        mode1 = 0
        if restart: mode1 |= 0x80
        if extclk: mode1 |= 0x40
        if ai: mode1 |= 0x20
        if sleep: mode1 |= 0x10
        if sub1: mode1 |= 0x08
        if sub2: mode1 |= 0x04
        if sub3: mode1 |= 0x02
        if allcall: mode1 |= 0x01
	logging.debug("Setting mode %02x" % mode1)
        self.bus.write_byte_data(self.addr0, self.REG_MODE1, mode1)
        return

    def setMode2(self, invrt = False, och = False, outdrv = True, outne = 0):
        mode2 = 0
        if invrt: mode2 |= 0x10
        if och: mode2 |= 0x08
        if outdrv: mode2 |= 0x04
        mode2 |= outne
        self.bus.write_byte_data(self.addr0, self.REG_MODE2, mode2)
        return
        
def test1():
    logging.basicConfig(level=logging.DEBUG)
    leds = PCA9685(bus = 1)
        
    for i in range(3):
        logging.debug("LEDs on")
        leds.setAllLED(1.0)
        time.sleep(2)
        logging.debug("LEDs off")
        leds.setAllLED(0)
        time.sleep(2)
    return

if __name__ == "__main__":
    test1()
