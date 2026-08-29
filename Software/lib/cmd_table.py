#^ cmd_GVar.py***************************************************************************
# *			Rhode Island Computer Museum (RICM)				*
# *				PICO ROBOT CAR						*
# * Version: 1.0									*
# * Date: 3/12/2026									*
# * By: Ray Young									*
# * For: Rhode Island Computer Museum (RICM)						*
# *											*
# *				COMMAND TABLE						*
# * This is just a table that contains necessary elements for the pattern mode needs to	*
# * operate. This table is used to validate the pattern file				*
# *											*
# * Elements:										*
# * 1st = Mnemonic code for the command, this is what is used in the pattern text file	*
# * 2nd = Display text for the command, can be used to list a pattern file		*
# * 3rd = Minimum decimal value for the command						*
# * 4th = Maximum decimal value for the command						*
# * 5th = # of packed bytes for the variable. 0 for novariables for the command		*
# * 6th = Name of function to call in cmd_funcs.py  !! MUST be defined in cmd_funcs !!	*
# *											*
# * Current commands:									*
# * S  = Set speed (0-100) 0 stops motors						*
# * L  = Make left turn at (S)peed							*
# * R  = Make right turn at (S)peed							*
# * F  = Move Fwd at (S)peed								*
# * B  = Move backward at (S)peed							*
# * BB = Begin a block definition 1-10							*
# * EB = End block definition								*
# * EX = Excecute a block (1-10)							*
# * W  = Wait in msec (0 - 65535)  0 to 65.535 seconds					*
# * Once you use the F,B,R,L commands, you need to set a wait to remain in that mode	*
# *											*
# * Requires cmd_funcs as CF to obtain the addr of each function			*
# * Some functions are currently under development and not yet implimented		*
# * Those functions are now pointing to a function called f_undefined in CMD_FUNCS.PY	*
#~ **************************************************************************************
import cmd_funcs as CF
#^ ***************************************************************************************
# *                                  COMMAND TABLE                                       *
# * This is just a table that contains necessary elements for the pattern mode needs to  *
# * operate                                                                              *
#                                                                                        *
# * Elements:                                                                            *
# * 1st = Mnemonic code for the command, this is what is used in the pattern text file   *
# * 2nd = Display text for the command, can be used to list a pattern file               *
# * 3rd = Minimum decimal value for the command                                          *
# * 4th = Maximum decimal value for a command                                            *
# * 5th = # of packed bytes for the variable. 0 for novariables for the command          *
# * 6th = Name of function to call in cmd_funcs.py  !! MUST be defined in cmd_funcs !!   *
#                                                                                        *
# Requires cmd_funcs as CF to obtain the addr of each function                           *
#~ ***************************************************************************************
entry_size = 6
CMD_TABLE = [
    "S","Set Speed%",0,100,1,CF.speed,
    "L","Make Left Turn",0,0,0,CF.lt,
    "R","Make Right Turn",0,0,0,CF.rt,
    "F","Move Forward",0,0,0,CF.fwd,
    "B","Move Backward",0,0,0,CF.bkwd,
    "LS1","Turn Left Signal-ON",0,0,0,CF.f_undefined,
    "LS0","Turn Left Signal-OFF",0,0,0,CF.f_undefined,
    "RS1","Turn Right Signal-ON",0,0,0,CF.f_undefined,
    "RS0","Turn Right Signal-OFF",0,0,0,CF.f_undefined,
    "HL1","Turn Headligh-ON",0,0,0,CF.f_undefined,
    "HL0","Turn Headligh-OFF",0,0,0,CF.f_undefined,
    "TL1","Turn Tail Light-ON",0,0,0,CF.f_undefined,
    "TL0","Turn Tail Light-OFF",0,0,0,CF.f_undefined,
    "BB","Begin Block",1,10,1,CF.block_begin,
    "EB","End Block",0,0,0,CF.block_end,
    "EX","Execute Block",1,10,1,CF.run_block,
    "W","Wait in ms",0,65535,2,CF.delay_ms
    ]   

#    "RL","Repeat Last Cmd",1,100,1,CF.repeat_last,
