#^ RICMMODE.PY **********************************************************************
# *                    RICM Mode change functions
# * Version: 1.0
# * Date:    3/20/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
# *
# * This is where mode get changed
# * Modifies a global variable NEW_MODE when changed
# * global variable BUTTON_PRESSED is set when the mode change button is pressed
# * Any running mode needs to check this variable to determine when to exit
# * Any mode cleanup is done by the mode that was running
#~ **********************************************************************************
from machine import Timer, Pin
import time
import globalv
# --------------------------------------------------------------------
#                  Blink New mode via independant timer
# --------------------------------------------------------------------
led2   = Pin("LED", Pin.OUT)  # use onboard PICO LED for mode display
xblink = globalv.new_mode*2   # temp value it holds cur_mode * 2 (on/off cycle)
xdelay = 6
xpause = xdelay   # period times to pause between blinks

#^ toggle_led ----------------------------------------------------
# This is called every PERIOD as defined by INIT function
# It toggles led on/off
#
def toggle_led(timer):
#~ ---------------------------------------------------------------
    global xblink, xpause
    if xblink == 0:   # pause mode 
       led2.value(0)  # turn off led 
       xpause -= 1    # decrement pause count
    else:
       led2.value(not led2.value())   # toggle it
       xblink -= 1    # decrment mode count

    if xpause == 0:  # are we done pausing? 
       xpause = xdelay    # yes - restore delay value
       xblink = globalv.new_mode*2  # and reload mode value (duty cycle is *2)
       
    return

#^ blikit --------------------------------------------------------
# set up blink of the onboard Pico LED to indicate mode
#
blinkt   = Timer()   # setup a timer called blink
in_flash = False
def blinkit(blink_on):
#~ ---------------------------------------------------------------
    global xblink, xpause

    if blink_on is True: 
       xblink = globalv.new_mode*2   # temp value it holds cur_mode * 2 (on/off cycle)
       xpause = xdelay   # period times to pause between blinks
       blinkt.init(mode=Timer.PERIODIC, period=250, callback=toggle_led)           
    else:
       blinkt.deinit()
       in_flash = False   # reset any flashing
    return

blinkit(True)         # make sure blink mode is running.this runs when module is loaded

#^ fast_toggle ---------------------------------------------------
# This will toggle the LED for the rapid flash rate
# it is called every period time as specified in flashit function
#
def fast_toggle(timer): 
#~ ---------------------------------------------------------------
    led2.value(not led2.value())
    return           

#^ flashit ------------------------------------------------------- 
# This will set up the onboard LED on the Pico to flash at a fast 
# rate to indicate an error. It can be called anytime, however 
# it will override the mode flashing timer  
# 
def flashit():
#~ ---------------------------------------------------------------
    if in_flash is False:
       blinkt.deinit()  # stop normal blinking
       blinkt.init(mode=Timer.PERIODIC, period=50, callback=fast_toggle)
       in_flasn = True
    return
    
# ----------------------------------------- end blink code -----------------------------------       

#^ *******************************************************************************************
# These functions:
#  led_off()
#  led_on_ms()
#  chamge_mode()
#  In ths module is where mode changes happen it is called from the MAIN.PY when pushbutton 
#  has been pressed the variable "button_pressed" has been set-up in the GLOBALV.PY module                      
#  Any running software needs the check "globalv.button_pressed" variable to determin if a mode   
#  change is requested                                                                      
#~ *******************************************************************************************

def led_off(seconds):
    led2.value(0)  # turn off LED
    time.sleep(2)     # for 2 seconds
    return

def led_on_ms(mills):    # flash led for milli seconds
    led2.value(1) # turn on LED
    time.sleep_ms(mills)   # for 125ms
    led2.value(0)     # turn it off - total time sleeping = 200ms
    return

def change_mode():    # come here when button pressed
    globalv.button_pressed
    blinkit(False)                  # turn off mode blink
    led_on_ms(2000)         # turn on LED for 2 seconds. We are in change mode routine
    xmode       = 0         # temp modem for routine
    button_wait = 2000      # only stay in this mode for 2000ms (2 sec)
    out_time    = time.ticks_add(time.ticks_ms(),button_wait)   # set end time for routine, safely

    globalv.button_pressed = False  # reset the button, wait for user to press again 

    while time.ticks_diff(out_time, time.ticks_ms()) > 0:  # Do while time has not elapsed
          if globalv.button_pressed is True:
             out_time    = time.ticks_add(time.ticks_ms(),button_wait)   # set end time for routine, safely 
             time.sleep_ms(300)   # switch debounce
             led_on_ms(125)         # turn on LED for 125ms
             xmode += 1     # increment mode value    
             if xmode > globalv.MAX_MODE:   # did we exceed maximum modes?
                xmode = 1                   # YES - Reset     

             globalv.button_pressed = False   # intr routine will set this to True
    if xmode == 0:                    # was mode changed?
       xmode = globalv.new_mode       # no - leave mode unchanged 
    print("New XMode:",xmode)
    globalv.new_mode = xmode     # store new mode
    led_off(2)   # turn off LED for 2 seconds
    blinkit(True)  # trun on mode blink
    return xmode
  
# ---------------- END changemode routine -------------------------------
