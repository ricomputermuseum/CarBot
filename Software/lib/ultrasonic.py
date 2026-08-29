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
# *    NORMAL                  =  0 
# *    ULTRASONIC_SENSOR_ERROR = -1
# *
# ***********************************************************************************
from machine import Pin, Timer, PWM
import time
import L9110 as motor
import globalv
import random
led2   = Pin("LED", Pin.OUT)

# return codes
NORMAL = 0
ULTRASONIC_SENSOR_ERROR = -1

ult = NORMAL

# global variables
TRIG = Pin(17,Pin.OUT)
ECHO = Pin(16,Pin.IN)

def init():
    while globalv.new_mode == globalv.COLLISION_AVOID:
        # if button is not pressed
        if globalv.button_pressed is False:
            globalv.cur_mode = globalv.new_mode
            
            # calc distance
            distance = distance_calc(TRIG, ECHO)
            print(distance)

            if distance == "ERROR":
                # return error code back to main
                return -1

            # make a movement decision
            distance_decision(distance)
            c = random.randint(1,10)
            
            # send to movement function depending on random number
            if c % 2 == 0:
                left_movement()
            else:
                right_movement()
            
            # give time for pico to run logic again
            time.sleep_ms(300)
        else:
            # if globalv.button_pressed is True:
            # stop moving the robot
            stop_movement()
            # return normal code
            return 0
    
def distance_calc(TRIG, ECHO):
    # calculate current distance
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()
    
    # create cutoff point in case module is not attached.
    # 30k microseconds is the max sensor range
    timeout_limit = 30000
    
    # initialize wait timer
    start_wait = time.ticks_us()
    
    while ECHO.value() == 0:
        # print("echo value 0")
        signal_off = time.ticks_us()
        # print(signal_off)
        # print("stuck")
    
    while ECHO.value() == 1:
        # if statement to handle module issues
        signal_on = time.ticks_us()
        if time.ticks_diff(signal_on, start_wait) > timeout_limit:
            print("error!")
            # stop robot in case its moving
            stop_movement()
            # flash led
            for i in range(100):
                # print("error")
                led2.value(1)
                time.sleep_ms(150)
                led2.value(0)
                time.sleep_ms(150)
            # return
            return "ERROR"
    
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

# stopping robot so we can exit back to main loop
def stop_movement():
    motor.drive(0, 0)

