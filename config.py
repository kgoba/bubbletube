import logging

LOGFILE = '/var/log/bubbletube.log'
LOGLEVEL = logging.INFO

T_ON_MIN = 0.05     # valve ON time at minimum adjustment
T_ON_MAX = 0.25     # valve ON time at maximum adjustment
T_OFF_MIN = 0.5     # valve OFF time at minimum adjustment
T_OFF_MAX = 5       # valve OFF time at maximum adjustment

RGB_IDLE_MIN = 0.01 # minimum RGB level at idle
RGB_IDLE_MAX = 0.12 # maximum RGB level at idle
RGB_TOUCH_ADD = 0.14    # RGB level to be added at touch
RGB_TOUCH_MUL = 3.00    # RGB level factor at touch

RGB_MAX = 0.5       # maximum RGB level at all times (don't exceed 0.5)

RGB_SPEED = 0.001   # how fast the RGB LED colors change

