#^ linefollow.py ------------------------------------------------------------------------
# *                      line follow Module
# * Version: 1.0
# * Date:    6/17/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
# *
# * Logic: LF_run() is the called function of this module that gets called from the main 
# *        module.
# *        Upon entry, it initializes the Analog to digital converter (ADC) and also 
# *        sets the pin to use for the LED that shines light onto the surface which
# *        reflects light back into Light Dependant Resistors or LDR, that is set up 
# *        as a voltage divider that is between 0-3.3v. 
# *        The LDR varies the voltage depending on the intensity of reflected light.
# *        This module constantly adjusts the sensitivity based upon reflected background 
# *        surface. For example the surface can be gray, brown, white etc. It will 
# *        automatically adjust the sensativity to determine what is a black line 
# *        or background intensity
# *
# * Return code is always 0
# * Entry Point:   LF_run()
# *
# * Dependants: 
# *             globalv
#~ --------------------------------------------------------------------------------------

import globalv

LFLED = Pin(16, Pin.OUT)    # Line Following LED Light Pin

LADC = machine.ADC(1)  # Which ADC to use for Left side LDR Sensor
RADC = machine.ADC(2)  # Which ADC to use for Right side LDR Sensor

def LF_run:
    AccumL = LADC.read_u16() / 256   # Initialize values. Read returns 0-65,535 value
    AccumR = RADC.read_u16() / 256   #    reduce resolution it to 0-255
    LFLED.value(1)   #  and turn LEDs on
                       
    while globalv.button_pressed is False and mode == LINE_FOLLOW:    
          SenseL = LADC.read_u16()   # read current L & R sensor values
          SenseR = RADC.read_u16()   #   0 - 65,535 value = 0 to 3.3v
      
          LV = float(SenseL) - AccumL)   # calculate blk/white diff
          RV = float(SenseR) - AccumR)
      
          if LV > RV:    # should we move to left?
             motor(50,100)     #  Yes  
          elif LV < RV:  # Should we move to right?
               motor(-50,100)  #  Yes
          else                 # Neither, stay on course 
             motor(0,100)      #  move forward           
                  # Re-calculate average ground color readings against which to detect sudden changes
             AccumL = (AccumL * 255 + SenseL) / 256   # make the range 0-256
             AccumR = (AccumR * 255 + SenseR) / 256

    motor(0,0)   # turn off motors
    LFLED.value(0)  #  and turn LEDs off
    return 0
