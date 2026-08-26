#^ RICMBOARD.PY *********************************************************************
# *                      RICM board Platform 
# * Version: 1.0
# * Date:    3/20/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
# *
# * Purpose: Establishes which platform we are using
# *
# * Also pulls in correct motor driver for platform
#~ **********************************************************************************
from machine import Timer, Pin
import globalv
import L9110 as motor   # using the L9110 motor driver

Name = "RICMboard"           # Name the platform we are using

# ------------------------ push button setup ------------------------
def button_press_int(pin):  # called each time button pressed
    global button_pressed   # defined in globalv
    globalv.button_pressed   = True  # set trigger
    return   # Any running software needs to check cur_mode = 0. if 0, mode is changing

# --- Establish the pushbutton interrupt service rtn ----------
button = Pin(14, Pin.IN, Pin.PULL_UP)   # use button on RICM Board
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_int)
