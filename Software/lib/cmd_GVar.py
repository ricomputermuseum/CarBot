#^ cmd_GVar.py***************************************************************************
# *			Rhode Island Computer Museum (RICM)
# *			        RICM CarBot
# * Version: 1.0
# * Date: 3/12/2026
# * By: Ray Young
# * For: Rhode Island Computer Museum (RICM)
# *
# Pattern mode global variables ----------------------------
#
# This file is needed for the pattern mode. The pattern mode heavily utilizes pointers
# usually singe byte pointers which would yeild up to 256 different commands.
# This is how the various pointers are used:
#
#cur_pat_ptr------/------> Pattern string         G.cmd_ptr--/---> CMD_TABLE
#nxt_pat_ptr-----/        (one or more bytes)               /      |-----cmd_nmemonic
#prv_pat_ptr----/           pat_cmd ---------------------->/       |-----cmd_display
#                           pat_var (1 or 2 byes if any)           |-----cmd_min
#                                                                  |-----cmd_max
#                                                                  |-----cmd_xbyte
#                                                                  |-----cmd_function
# * pat_ptr are merely pointers into the pattern string
#
# pat_cmd is an index into CMD_TABLE same as cmd_Gvar_ptr
# pat_var are 1 or two bytes indicating a 8 or 16 bit integer
#
# cmd_nmemonic is the command that is used in uploaded patten file
# cmd_display is the long name of the command
# cmd_min is the min value for the command if the command has variables
# cmd_max is the maximum value for a command
# cmd_xbyte is how many more bytes is needed after the command
# cmd_function is a pointer to the function that handles the actual command when running
#~ **************************************************************************************

pattern       = ""    # actual pattern string in memory
prv_pat_ptr   = 0     # prev command for repeat func
cur_pat_ptr   = 0     # current pattern pointer
nxt_pat_ptr   = 0     # next pattern pointer 

block_amt     = 10    # how many blocks can we have?   
block_table   = [0] * (block_amt+1) # this array is indexed by block #, value in array is index into pattern string
                                    # 0 = not defined, > 1 = index of begining of block   
in_block      = 0      # block number being defined
skip_cmd      = False  # this is an indicator to skip over any block definitions while executing a pattern
cmd_nmemonic  = ""     # Command Mnemonic from CMD_TABLE
cmd_display   = ""     # Command display string from CMD_TABLE
#cmd_var       = 0      # this is the actual variable thats after a command. Created by set_gvar in cmd_funcs.py
cmd_ptr       = 0      # index into CMD_TABLE or -1 if command not valid
cmd_no_xbyt   = 0      # number of extra bytes for command from CMD_TABLE
cmd_function  = ""     # function to call for current command from CMD_TABLE
#ptr_idx       = 0
ivar          = 0      # command variable actual value created by set_gvar in cmd_funcs.py

#^ Clearing pattern elements ----------------------------------------------------------
# This function is called to reset various pointers and the return the pattern string to be empty
# after this function is called, garbage collection should done
#
# Function returns nothing
#
def clear_pattern():
#~ ------------------------------------------------------------------------------------
    pattern       = ""    # actual pattern string in memory
    prv_pat_ptr   = 0     # prev command for repeat func
    cur_pat_ptr   = 0     # current pattern pointer
    nxt_pat_ptr   = 0     # next pattern pointer 
    in_block      = 0
    cmd_nmemonic  = ""     # Command Mnemonic from CMD_TABLE
    cmd_display   = ""     # Command display string from CMD_TABLE
    cmd_ptr       = 0      # index into CMD_TABLE or -1 if command not valid
    cmd_no_xbyt   = 0      # number of extra bytes for command from CMD_TABLE
    cmd_function  = ""     # function to call for current command from CMD_TABLE
    ivar          = 0      # command variable actual value created by set_gvar in cmd_funcs.py
    x             = 0      # block index 
    while x <= block_amt:
          block_table[x] = 0
          x += 1
    return      
                      
