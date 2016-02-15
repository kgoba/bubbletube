#!/usr/bin/env python

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
    while True:
        pass
    return
    
if __name__ == "__main__":
    main(sys.argv)
