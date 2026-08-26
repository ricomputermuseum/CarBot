#^ MAIN.PY ******************************************************************************
# *			Rhode Island Computer Museum (RICM)
# *				    RICM CarBot
# * Version: 1.0
# * Date: 3/12/2026
# * By: Ray Young
# * For: Rhode Island Computer Museum (RICM)
# *
# * This is the main program for a simple robot car
# * its modular in design so it can use many different motor driver boards & Platforms
# * provided that a driver for the board is written
# * A platform is capable of using many external motor drivers or use onboard drivers
# *
# * There are also three platforms that can be used:
# * 1. RICM Pico breakout board designed by Grant Koboszka@RICM
# * 2. RoBro - a single board robot also designed by Grant Koboszka@RICM. Has built in sensors
# * 3. picobreakout - similar to the RICM board but uses external motor driver
# *
# * Currently there are two motor driver boards:
# * 1. FEETECH simple two motor board
# * 2. L9110 RICM custom board with onboard L9110 chips as motor drivers
# *
# * Currently the program can control the robot in 4 different modes 
# * 1 - Remote control. By using any web browswer, the user can control the car via
# *     a joystick type of control   
# * 2 - Line following. By drawing a dark line with a magic marker, the robot will
# *     follow alog the line (not yet implimented)
# * 3 - Collisin avoidence. With an ultrasonic module, the car will autonumously
# *     drive on the ground avoiding any obsticals it encounters. Using the Ultrasonic
# *     sensor, it senses the distence of an object, stops, turns, and detects
# *     if it can move in that direction. if not, it turns again, until no object
# *     is in its path. It will ten continue forward until another object is detected
# * 4 - Follow a Pattern. The robot will move along an upload pattern, using various
# *     pattern plans. The user can upload a pattern to the robot where it will stay
# *     until it is overwritten by a new one. Read documentation for the various
# *     commands you can give it
# * Mode selection is done via an onboard pushbutton on the custom RICM board.
# * Modes can be changed at anytime
# *
#~ **************************************************************************************

import globalv                 # load global values
Platform = __import__(globalv.platform)  # load whatever platform is needed
# import ricmboard as Platform
import time                    # time functions
from machine import Timer, Pin
import gc                      # garbage collection. we will run manually
import ricmmode                # code for mode switching
# ------------------ import all the mode modules -----------------
import Remote                  # Remote control module
import Pattern                 # Pattern following module

try:
   import linefollow          # attempt to load Line Following Module
   LF = True                  # This mode requires additional hardware  
except ImportError:
   LF = False  
     
try:
   import ultrasonic          # attempt to load Collision avoidance module
   Ultra = True               # This mode requires additional hardware 
except ImportError:
   Ultra = False 
     
# ***************************** HERE WE GO! **************************
# Modes will be set via interrupt push button
# ********************************************************************

# ----------------------------- INITIALIZE ----------------------
# Platform  = __import__(globalv.Platform)  # which platform using
rc = Platform.motor.init()     # initialize motor controller
print("Mem allocated:", gc.mem_alloc(), "Free:",gc.mem_free())
print("Platform:",Platform.Name)
print("Motor Driver:",Platform.motor.Name)
x     = time.localtime()
date  = str(x[1])+"/"+str(x[2])+"/"+str(x[0])
ltime = f"{x[3]:02d}:{x[4]:02d}"
print("Current Date/Time:",date,ltime,"\r\n")

# Mode setting will be done anytime if using the RICM board via a push button,
# with default mode = REMOTE
# ------------------------ MAIN CODE -----------------------------
once = False          # this is to only display the mode ONCE on the console
while True:     
     if globalv.button_pressed is True:    # was button pressed?
        print("Changing mode..")           # Yes
        globalv.new_mode = ricmmode.change_mode()          # new mode is set here
        print("New Mode:", globalv.new_mode)
        once = False
 
# -------------- MODE-1(remote control) -----------------
     elif globalv.new_mode == globalv.REMOTE:    # is the mode = remote control?
       rc = Remote.RemoteMode(Platform.motor)         # yes - do web remote control
       print("Remote RC:",rc)

# -------------- MODE-2(Line follow) ------------------
     elif globalv.new_mode == globalv.LINE_FOLLOW:
         if once is False:
            if LF is True:
               print("Entering line following mode.")
            else:   
               ricmmode.flashit()      # we can rapid flash the led here
               once = True
         
# -------------- MODE-3(Coll Avoid) ------------------
     elif globalv.new_mode == globalv.COLLISION_AVOID: 
         if once is False:
            print (Ultra) 
            if Ultra is True:  
               print("Entering Collision avoidence mode.")
               rc = ultrasonic.init()     # Call ultrasonic code
            else:
               rc = -1  
            if rc < 0:                 # was the return code NORMAL
               if globalv.debug is True:
                  print("Ultrasonic module not connected") 
               ricmmode.flashit()      # NO - we can rapid flash the led here
            once = True   
         
# -------------- MODE-4(Patt Follow) ------------------         
     elif globalv.new_mode == globalv.PATTERN:
          print("Entering PATTERN mode.")
          rc = Pattern.get_pattern()
          print("Pattern RC:",rc)

     else:
         print("Unknown mode. Mode:", globalv.new_mode)  # should never happen.....
         time.sleep(5)
         
