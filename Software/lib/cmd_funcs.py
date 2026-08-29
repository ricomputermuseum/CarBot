#^ CMD_FUNCS.PY *************************************************************************
# *			Rhode Island Computer Museum (RICM)				*
# *				PICO ROBOT CAR						*
# * Version: 1.0									*
# * Date: 3/12/2026									*
# * By: Ray Young									*
# * For: Rhode Island Computer Museum (RICM)						*
# *											*
# * This module is where all the routines are for the PATTERN function			*
# * The function name need to apear in the CMD_TABLE.PY so that the table can locate	*
# * the correct process to run when they apear in the pattern file			*
# * A repeat function is being worked on here but currently not implimented		*
# *											*
#~ **************************************************************************************
import globalv
import cmd_GVar as G
import time
import cmd_table as CT
import ricmboard as Platform   # which platform are we using?
from array import array

# ------------------- Command funcs ---------------------
# Make sure ALL functions are defined in CMD_TABLE
# -------------------------------------------------------

Throttle        = 0       # speed for any wheel movements
#prev_cmd_idx   = 0       # previous command 

# *****************************
# * Repeat table has a chain of commands that need to be repeated
# * ie a RL command was detected, an entry is appended. in each entry is the index into pattern string
# * and the number of times to repeat that entry
# * If the RL was issued for a execute block and within the block it ALSO has a repeat command
# * there had to be a way to handle nested repeats like that
# * If a RL command was to run a previous RL command, it will repeate the last valid command
# * ie EX 1, RL3, RL5 will repeat EX 1 8 times
# ****************************
repeat_table = array('I',[0,0,0,0])  # crreate an array of unsigned int
    
# block chain = runing blocks, index is block number, contents = pntr to cmd to jump to after block executed
block_chain = [0] * (G.block_amt+1)

#^ set_gvar******************************************
# obtain command pointed to by cur_pntr
# set global variables with nmemonic, operand (if any) & function
# operands can be 1 or two bytes as indicated in CMD_TABLE
# return next index into pattern string after current command
def set_gvar(pattern_index):
#~ ******************************************
    G.cur_pat_ptr  = pattern_index       # save this as the current pointer into pattern string
    ri             = pattern_index       # save return index. ri is index into pattern string   
    cmd_index      = G.pattern[ri]         # get the index into CMD_TABLE for command
    G.cmd_no_xbyt  = CT.CMD_TABLE[ord(cmd_index)+4] # get the number bytes for the variable (if any)    
    G.cmd_function = CT.CMD_TABLE[ord(cmd_index)+5] # get function to run    
    G.cmd_nmemonic = CT.CMD_TABLE[ord(cmd_index)]        # save the command nmemonic  
    ri            += 1   # point to next byte in patter string
    G.ivar         = -1  # set default operand value. Operands CAN have a ZERO value, so we use -1
    if G.cmd_no_xbyt > 0:
       G.ivar = ord(G.pattern[ri])     # get variable
       ri    += 1   # point to next byte in pattern string
    if G.cmd_no_xbyt == 2:
       G.ivar = (G.ivar*256)+ord(G.pattern[ri])
       ri    += 1    # last bump s/b next command     
    return ri 
       
#^ speed -----------------------------------------------------------
# sets the speed to use for all further commands 
def speed(valu):
#~ -----------------------------------------------------------------
    global Throttle
    Throttle = valu
    print("Set throttle to",valu,"%")
    if valu == 0:
       Platform.motor.drive(0,0)  # move fwd   
    return G.nxt_pat_ptr   # just return cmd pointer
    
#^ Left turn -------------------------------------------------------
# Make motors make a left turn at the current speed 
# X is not used...
def lt(x):
#~ -----------------------------------------------------------------
    print("Left turn")
    Platform.motor.drive(-100,Throttle)   # left turn
    return G.nxt_pat_ptr   # just return cmd pointer
    
#^ Right turn -----------------------------------------------------
# Make motors turn right at the current speed
# X is ignored 
def rt(x):
#~ ----------------------------------------------------------------
    print("Right turn")
    Platform.motor.drive(100,Throttle)    # Right turn
    return G.nxt_pat_ptr   # just return cmd pointer
    
#^ Forward -------------------------------------------------------
# Make the robot move forward at the current speed
# X is ignored 
def fwd(x):
#~ ---------------------------------------------------------------
    print("Move FWD")
    Platform.motor.drive(0,Throttle)  # move fwd
    return G.nxt_pat_ptr   # just return cmd pointer
    
#^ Backward ------------------------------------------------------
# Moves the robot backward at the current speed
# X is ignored
def bkwd(x):
#~ ---------------------------------------------------------------
    print("Move BWD")
    Platform.motor.drive(0,1-Throttle-1)
    return G.nxt_pat_ptr   # just return cmd pointer

#^ Undefined function --------------------------------------------
# This function does nothing, it returns the next command pointer
# X is not used
def f_undefined(x):
#~ ---------------------------------------------------------------
    return G.nxt_pat_ptr

#^ Begin block ---------------------------------------------------
# This function skips over a block definition as it not executable
# It reads to the EB code and return the next command pointer
# X is not used
def block_begin(x): 
#~ ---------------------------------------------------------------- 
    if globalv.debug:
       print("Skipping block",x,"definition")
    skip = True     # set skip flag
    while skip is True:
          G.nxt_pat_ptr = set_gvar(G.nxt_pat_ptr)    # get next command, based in current pattern pointer          
          if G.cmd_nmemonic == "EB":  # is the current nmemonic = End of Block? 
#             G.next_pat_ptr = set_gvar(G.cur_pat_ptr)   # go past the EB command
             skip = False            # yes - we are done skipping the block. 
#          G.next_pat_ptr = set_gvar(G.nxt_pat_ptr)   # go past the EB command, point at next command                  
    return G.nxt_pat_ptr        # return the pattern pointer AFTER the EB command

#^ End Block -----------------------------------------------------
# X is not used
# Just return the next pointer after the EB command
def block_end(x):
#~ --------------------------------------------------------------- 
    G.nxt_pat_ptr = block_chain[G.in_block]   # restore pointer
    if globalv.debug:
       print("At EB:",G.in_block,G.nxt_pat_ptr)                     
    return G.nxt_pat_ptr   # where to go now.........

#^ Execute Block -------------------------------------------------
# X is the block number to run
# check for block already in use
# if used, ignore the EX cmd 
# add item to block chain 
# update in_use array that new block will be running
# save the next command index
# find the block and run it
# upon return cur_pat_ptr must point to the EX command
#
def run_block(x):
#~ ---------------------------------------------------------------  
    block_chain[x] = G.nxt_pat_ptr             # Save next command index into pattern string
                                                   # indicates that block is executing
    if globalv.debug:
       print("Saved next command ptr after EX command",block_chain[x]) 
    G.in_block = x            # save the block number thats running
    if globalv.debug:
       print("Running block",x,G.block_table[x])
    G.nxt_pat_ptr = G.block_table[x]    # load pat ptr from block table indexed by x   # added RTY     
    return G.nxt_pat_ptr    # return where in pattern string to run

# ---------------------------------------------------------------------------------- Repeat Last
# Repeat is like a stack. pushed on the stack is the NEXT command
# the CURRENT cmd is repeated
# if ANOTHER repeat is encountered right after each other, the old cmd is still repeated, but
# the return command is the NEXT command.
# the only way an OLD command gets updated is when its NOT a repeat command

# NOTES:
# repeat[]
#   	        return_pat_ptr (int)  points to next operation AFTER the RL operation
#	        repeat_count   (int)
#	        repeat_operation(ptr into cmd_tble) (int)
#	        repeat_operand (int) 
# len(repeat)-->
# 	
# each entry has 4 elements
# index 0,4,8,12, etc.
#
# x = len(repeat)  will point to 13 if the array has 12 elements on it
# 
# so........
#    repeat_operand   = repeat(cmd-1)
#    repeat_operation = repeat(cmd-2)
#    repeat_count     = repeat(cmd-3)
#    repeat_pat_ptr   = repeat(cmd-4)
#
# always keep 0,0,0,0 as the first element   
# if next cmd is also a repeat, just update count, and continue. do NOT pop off the stack.
# else get return_pat_ptr, make it cur_pat_ptr
#
# if len(repeat) != 4 pop 4 times
# return

    
def x_repeat_last(x): # code to run the previous command X times 
   
    print("Repeat code....",x,G.prv_pat_ptr,G.cur_pat_ptr,G.nxt_pat_ptr) 
    
    # ****************************************
    # Handle a repeat last condition
    # ****************************************
    # save index into pattern string to repeat  
    # X has the amount of times to repeat a command
    # G.cur_pat_ptr has the current (RL) index into pattern table
    # Once repeat function completes go past the RL command
    # Check if its anoth RL command. if so, stay here until the current command is NOT an RL command
    # Once next command is NOT a repeat go back one index in repeat_table and repeat...
    # Exit ONLY when you are back to index ZERO in repeat_table
    # This allows for nested repeats
    
    print("Len before extend table",len(repeat_table))    # impliment a stack of repeats
    repeat_table.extend([G.prv_pat_ptr,G.cur_pat_ptr,G.ivar])

    print("in repeat.....", G.prv_pat_ptr,G.cur_pat_ptr,G.ivar)   # cur_pat_ptr is the RL and ivar is the variable

#    cur = len(repeat_table)
#    repeat_table[cur] = G.prev_idx
    rpt_cmd      = len(repeat_table) 

    after_repeat = G.cur_pat_ptr       # this is the index into pattern string of the repeat command
    
    rep_last  = rpt_cmd-2          # the variable cmd is the pointer into repeat_table
    print("Repeat",rep_last,",",G.ivar,"times")        # show pattern ptr to repeat

    no_use    = set_gvar(rep_last)    # get the index into pattern string of command to repeat 
#    print("repeat command:",last_array-2)
    func2run  = G.cmd_function
    loop_ctr  = x
    while loop_ctr > 0:
          ret     = set_gvar(rep_last)
          G.nxt_pat_ptr = func2run(G.ivar)   # try the command. send a variable even if not used
          loop_ctr -= 1                                   
    
    print("retoring after repeat",after_repeat)
    print("len of repeat_table",len(repeat_table))
    repeat_table.pop()   # remove last 3 entries of repeat_table
    repeat_table.pop()    
    repeat_table.pop()  
    print("Len of repeat_table after pop",len(repeat_table))  

#    G.nxt_cmd_ptr = set_gvar(after_repeat)
    print("Leaving repeat. next cmd:",G.nxt_pat_ptr)              
    return G.nxt_pat_ptr   # just return cmd pointer

#^ Wait ----------------------------------------------------------
# This function will just issue a time.sleep_ms
# X is the time in MS to wait
# Function returns next command pointer
#   
def delay_ms(x):
#~ ---------------------------------------------------------------
    print("Wait",x,"ms")
    time.sleep_ms(x)
    return G.nxt_pat_ptr   # just return cmd pointer    
