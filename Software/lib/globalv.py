#^ GLOBALV.py ***********************************************************************
# * Contains GLOBAL VALUES across all modules
# *
# * Version: 1.0
# * Date:    3/20/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
#~ **********************************************************************************
import sys

Robot_Name      = "Robot007"     # Name of Robot. its also the AP_SSID and same as password
                                 # make sure between 8 and 32 characters with NO spaces 
Robot_Passwd    = Robot_Name     # make SSID password the same as robot name

Robot_URL       = "robot.run"    # this is the name used to connect via web interface

Platform        = "ricmboard"     # this is the platform that is being used, platform also import motor drvr

debug           = False           # used to display variables during debugging

# --------------- Modes of operation DO NOT CHANGE THESE VALUES!! These are constants! ------
REMOTE          = 1
LINE_FOLLOW     = 2
COLLISION_AVOID = 3
PATTERN         = 4
MAX_MODE        = 4
# -------------------------------------------------------------------------------------------

button_pressed  = False      # used for mode changes. it is set by button ISR in Platform, ie ricmboard
cur_mode        = 0          # MODE current mode
new_mode        = REMOTE     # Default mode - can be chaanged by pushbutton

# ------------------------- Convert text URL to a DNS URL -----------------------
dot_idx      = Robot_URL.find(".")    # look for the "." in URL
txt1         = chr(dot_idx) + Robot_URL[:dot_idx]
txt          = txt1 + chr(len(Robot_URL) - dot_idx-1) + Robot_URL[dot_idx+1:]
wurl         = txt.encode()   # set global variable for DNS lookup. used in web_stuff module for web connections
