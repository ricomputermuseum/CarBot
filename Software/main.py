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
# * 3. picobreakout - similar to the RICM board but uses external motor driver ie. FeeTech
# *
# * Currently there are two motor driver boards:
# * 1. FEETECH simple two motor board
# * 2. L9110 RICM custom board with two onboard L9110 chips as motor drivers
# *
# * Currently the program can control the robot in 4 different modes 
# * 1 - Remote control. By using any web browswer, the user can control the car via
# *     a joystick type of control   
# * 2 - Follow a Pattern. The robot will move along an upload pattern, using various
# *     pattern plans. The user can upload a pattern to the robot where it will stay
# *     until it is overwritten by a new one. Read documentation for the various
# *     commands you can give it
# * 3 - Collision avoidence. With an ultrasonic module, the car will autonumously
# *     drive on the ground avoiding any obsticals it encounters. Using the Ultrasonic
# *     sensor, it senses the distence of an object, stops, turns, and detects
# *     if it can move in that direction. if not, it turns again, until no object
# *     is in its path. It will ten continue forward until another object is detected
# * 4 - Line following. By drawing a dark line with a magic marker, the robot will
# *     follow alog the line (not yet implimented)
# * Mode selection is done via an onboard pushbutton on the custom RICM board.
# * Modes can be changed at anytime
# *
#~ **************************************************************************************

import globalv                 # load global values
# import ricmboard as Platform
import time                    # time functions
from machine import Timer, Pin
import gc                      # garbage collection. we will run manually
import Remote                  # Remote control modual
import Pattern                 # Pattern following module
import ricmmode                # code for mode switching

try:
   import linefollow          # attempt to load Line Following Module
   LFunc = linefollow.LF_run             # This mode requires additional hardware  
except ImportError:
   LFunc = ricmmode.flashit  
     
try:
   import ultrasonic          # attempt to load Collision avoidance mode
   CAFunc = ultrasonic.init              # This mode requires additional hardware 
except ImportError:
   CAFunc = ricmmode.flashit 
          
#               MODES Table
# Table entries: Mode number, Function to call
#
# Add tale entries for new functions...
#
MODE_TABLE = [
	1,Remote.RemoteMode,    # Remote control
	2,Pattern.get_pattern,  # Pattern follow
	3,CAFunc,               # Collision Avoidance
	4,LFunc                 # Line Following (not implimented)
	] 

# ***************************** HERE WE GO! **************************
# Modes will be set via interrupt push button
# ********************************************************************

# ----------------------------- INITIALIZE ----------------------
# Platform  = __import__(globalv.Platform)  # which platform using
rc = globalv.Platform.motor.init()     # initialize motor controller
print("Mem allocated:", gc.mem_alloc(), "Free:",gc.mem_free())
print("Platform:",globalv.Platform.Name)
print("Motor Driver:",globalv.Platform.motor.Name)
x     = time.localtime()
date  = str(x[1])+"/"+str(x[2])+"/"+str(x[0])
ltime = f"{x[3]:02d}:{x[4]:02d}"
print("Current Date/Time:",date,ltime,"\r\n")

# Mode setting will be done anytime if using the RICM board via a push button,
# with default mode set in globalv.py
# ------------------------ MAIN CODE -----------------------------
once = False          # this is to only display the mode ONCE on the console
while True:
  
    if globalv.button_pressed is True:    # was button pressed?
       print("Changing mode..")           # Yes
       globalv.new_mode = ricmmode.change_mode()          # new mode is set here
       print("New Mode:", globalv.new_mode)
       once = False

    if globalv.new_mode == 0 or not globalv.Robot_Name: 
       ricmmode.led2.value(1)
    else:   
#---------------------- MODE Selecion (cycles thru MODE_TABLE)
       xmode = 0     # begin at the first element of the MODE_TABLE
       mlen  = len(MODE_TABLE)/2    # Number of table entries
       while xmode < mlen:    # each entry in mode table is 2 elements
             if MODE_TABLE[xmode] == globalv.new_mode:   # compare table mode number to current mode
                func = MODE_TABLE[xmode+1]    # extract the function to call from table
                rc   = func()     # do function in MODE_TABLE
             # ------------- check return code
                if rc != 0:      # normal function codes are 0, anything negative is an ERROR, anything positive is a status
                   print("Return code from Function:",rc)
                xmode = mlen  # get out of the while loop
             xmode += 2       # point to next entry        
