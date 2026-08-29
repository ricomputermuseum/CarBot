#^ L9110.py *************************************************************************
# *                      L9220 Motor Driver for Pico-2W                             *
# * Version: 1.0                                                                    *
# * Date: 3/20/2026                                                                 *
# * By: Ray Youg                                                                    *
# * For: Rhode Island Computer Museum (RICM)                                        *
# *                                                                                 *
# * Logic: Motor driver has two parts:                                              *
# *        1 - Motor initialization  (init)                                         *
# *        2 - Motor Drive           (drive)                                        *
# *                                                                                 *
# * Motors are connected via GPIO pins.This driver uses 2 pins for each driver      *
# * Left L9110  Connected to GPIO-21 (pin-27) & GPIO-20 (pin-26)                    *
# * Right l9110 connected to GPIO-19 (pin-25) & GPIO-18 (pin-24)                    *
# * To drive motors, each motor gets a value of -100 to 100 with 0 bring stop       *
# * Because of limitations of the Pico, values will be in increments of 10          *
# * The driver will use these values to drive each motor.                           *
# *                                                                                 *
# * Use a return code to indicate sucess (0) or failure (negative value)            *
# * So calling program can determine                                                *
# *                                                                                 *
# * Future versions may include a tachometer function to keep motors in sync        *
# *                                                                                 *
#~ **********************************************************************************
from machine import Pin, PWM
import globalv as G
Name = "L9110"

#    pin here means a = GPIO number
#    Motors are PWM controlled  was 45khz
RwheelA = PWM(Pin(19), freq=40, duty_u16=0)  # Wheel Motor R-Side as PWM 
RwheelB = PWM(Pin(18), freq=40, duty_u16=0)
    
LwheelA = PWM(Pin(21), freq=40, duty_u16=0)  # Wheel Motor L-Side as PWM
LwheelB = PWM(Pin(20), freq=40, duty_u16=0)


# ************************************************************************
# *                   Initialze motor driver                             *
# ************************************************************************
def init():
  # nothing to do, motors alredy setup above  
    return 0
    
# ************************************************************************
# *                      Drive the motors                                *
# ************************************************************************

def drive(d, t):
    if G.debug:
       print(Name,"-",d,t) 
    # t = throttle -100 to 100     (Bak = 100, Fwd = 100)
    # d = differential -100 to 100 (left = -100, right = 100)
    #
    #                 A B 
    # motor Clockwise 0 1
    #       Counter   1 0
    #       Stop      0 0
    #
    # ------ PWM Values are from 0 - 65535
    # ------ X & Y will be -100 to 100 Horiz & vertical Zero is center position (STOP position)
    adjfactor = 655.35     # For L9110, this will be added to values to update the PWM  
    # For a two-wheeled robot, the X and Y inputs are converted into left and right wheel speeds.
    # y = Throttle
    # x = Differential
    Rwheel  = t + d          # do wheel diffential                                                            
    Lwheel  = t - d                                                                       
      
    # Dont exceed limits of motor controller
    Lwheel = max(-100, min(100, Lwheel))
    Rwheel = max(-100, min(100, Rwheel))
             
    Rwheel = int(round(Rwheel*adjfactor))   # adjust values to be 0-65535 rather than 0-100
    Lwheel = int(round(Lwheel*adjfactor))

    if Rwheel > 0:               # Fwd Direction
       RwheelA.duty_u16(Rwheel)
       RwheelB.duty_u16(0)
    else:
       RwheelA.duty_u16(0)       # Bak Direction
       RwheelB.duty_u16(1-Rwheel)
   
    if Lwheel > 0:               # Fwd Direction
       LwheelA.duty_u16(Lwheel)
       LwheelB.duty_u16(0)
    else:
       LwheelA.duty_u16(0)       # Bak Direction
       LwheelB.duty_u16(1-Lwheel)
    
    return 0      # Zero indicates sucess, negative value means error, positive values mean valid response codes

# --------------------------------------------- END DRIVER SECTION ----------------------------------------------
