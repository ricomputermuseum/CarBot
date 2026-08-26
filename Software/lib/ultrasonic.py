# ***********************************************************************************
# *                      Collision avoidance via ultrasonic sensor
# * Version: 1.1
# * Date: 5/17/2026
# * By: Nicole Evans
# * For: Rhode Island Computer Museum (RICM)
# *
# * Logic: Determines distance by using the ultrasonic sensor
# * and moves the motors based on distance calc
# *
# * Return codes from this module:
# *    NORMAL =  0
# ***********************************************************************************
from machine import Pin, Timer, PWM
import time
import L9110 as motor
import globalv
import random

# return codes
NORMAL = 0

ult = NORMAL

# global variables
TRIG = Pin(17,Pin.OUT)
ECHO = Pin(16,Pin.IN)

def init():
    # if button is not pressed
    while globalv.button_pressed is False:
#        globalv.cur_mode = globalv.new_mode
        
        # if globalv.button_pressed is False and ult == NORMAL:
        
        # calc distance
        distance = distance_calc(TRIG, ECHO)
        print("Distance:", distance)
        if distance == 0:   # Ultrasonic not installed
           stop_movement()  # just in cae we were moving
           return -1

        # make a movement decision
        distance_decision(distance)
        c = random.randint(1,10)
        
        # send to movement function depending on random number
        if c % 2 == 0:
            left_movement()
        else:
            right_movement()
    else:
        # if globalv.button_pressed is True:
        stop_movement()
        return 0   # NORMAL return code
    
def distance_calc(TRIG, ECHO):
    # calculate current distance
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    timeout_limit = time.ticks_us() + 30000  # 30ms window limit use for timeout
    
    while ECHO.value() == 0:
          signal_off = time.ticks_us()
          if time.ticks_us() > timeout_limit:
             return 0  # Pin stayed LOW; sensor is missing/disconnected, return NO Distance
    
    while ECHO.value() == 1:    
        signal_on = time.ticks_us()
    
    time_passed = signal_on - signal_off
    # do conversion to get distance in cm
    distance = (time_passed * 0.0343) / 2
    print(distance)
    return distance

def distance_decision(distance):
    # if robot is close to an object:
    if distance <= 30:
        
        # stop initially
        motor.drive(0,0)
        time.sleep_ms(200)
        # move backwards for a little bit
        motor.drive(0, -50)
        time.sleep_ms(500)
            
        # randomly select which way to go
        c1 = random.randint(1,10)
        if c1 % 2 == 0:
            motor.drive(-75, -75)
            time.sleep_ms(500)
        else:
            motor.drive(75, 75)
            time.sleep_ms(500)

    # if not close to an object, make a random movement
    else:
        c = random.randint(1,10)
        # 
        if c % 2 == 0:
            left_movement()
        else:
            right_movement()
               
# function for robot moving slightly to the left
def left_movement():
    motor.drive(-10, 75)
    
# function for robot moving lightly to the right
def right_movement():
    motor.drive(30, 75)

def stop_movement():
    motor.drive(0, 0)
