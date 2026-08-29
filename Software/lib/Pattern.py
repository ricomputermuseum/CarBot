#^ cmd_pattern.py -----------------------------------------------------------------------
# *                      Pattern follow Module                                          *
# * Version: 1.0                                                                        *
# * Date:    6/17/2026                                                                  *
# * By:      Ray Youg                                                                   *
# * For:     Rhode Island Computer Museum (RICM)                                        *
# *                                                                                     *
# * Logic: get_pattern() in this module is the main function that gets                  *  
# *        called from the main module                                                  *
# *        When called, it sets up a WiFi Access Point(AP), DNS server, HTTP server     *
# *        The DNS server will intercept ALL DNS requests and ONLY respond to           *
# *        "ricm.run" as defined in globalv.py module.                                  *
# *        The user MUST connect to the AP whos SSID/Password are defned in globalv.py  *
# *        Once connected to the AP, the user opens a web browser, and enters           *
# *        "ricm.run" into the URL line.                                                *
# *        The HTTP server then responds with the root web page (pttern.html) standard  *
# *        file selection dialog. As the file is loading, each line is sent to tihs     *
# *        module for validation. If any error is encountered, the error is displayed   *   
# *        and pattern load is terminated.                                              *
# *        upon sucessful load the robot will execute the pattern file repeatedly.      *
# *                                                                                     *
# * Return codes are implimented as a table that can be accessed by name or code via    *
# * error_func(valu). if you sed a valu that is text, it will reply with a code. If a   *
# * code is sent, function will return the test of the error                            *  
# *                                                                                     *
# * Entry Point:   get_pattern()                                                        *
# *                                                                                     *
# * Check return_codes.py for all available return codes from this module               *
# *                                                                                     *
# * Dependants: json  (std uPython)                                                     *
# *             globalv                                                                 *
# *             cmd_GVar  as G                                                          *
# *             cmd_table as CT                                                         *
# *             web_stuff as WS                                                         *
# *             ricmboard as Plaform                                                    *
# *             gc (std uPython)                                                        *
# *                                                                                     *
#~ --------------------------------------------------------------------------------------


import json                    # STD uPthon JSON Object handleing
import globalv                 # RTY Global variables across all modules
import cmd_GVar as G           # RTY Pattern variables
import cmd_table as CT         # RTY Command tables 
import web_stuff as WS         # RTY Web_Stuff module (routines for AP,DNS,HTTP)
#import ricmboard as Platform   # which platform are we using?
import gc                      # STD Garbage collection

# ======================================================
# Possible return codes
# ======================================================
ERROR_TABLE = [
      "NORMAL",                                   0,
      "NON_NUMERIC_VALUE",                       -1,
      "BLOCK_LEFT_OPEN",                         -2,
      "NO_OPEN_BLOCK",                           -3,
      "INVALID_COMMAND",                         -4,
      "VARIABLE_EXPECTED",                       -5,
      "VALUE_OUT_OF_RANGE",                      -6,
      "NESTED_BLOCK",                            -7,
      "BLOCK_ALREADY_DEFINED",                   -8,
      "UNDEFINED_ERROR",                         -9,
      "BLOCK_NOT_DEFINED",                       -10,
      "NO_BLOCK_EXECUTION_WITHIN_BLOCK_ALLOWED", -11,
      "KEYBOARD_INTERRUPT",                      -12,
      "BROWSER_CLOSED",                          -13
]

#^ ====================================================
# ERROR TABLE funtions. either lookup by txt or number
#               
def error_func(var):
#~ ====================================================
    try:
        x = ERROR_TABLE.index(var)
    except ValueError:
        x = -1

    if isinstance(var,str):
       if x != -1: 
          rv = ERROR_TABLE[x+1]
       else:
          rv = -99 
    else:
       if x != -1:
          rv = ERROR_TABLE[x-1]
       else:
          rv = "UNDEFINED_ERROR" 
    return rv
# ----------------------------------------------------

NORMAL = error_func("NORMAL")    # defailt return code

UP      = True
DOWN    = False
line_no = 1
pattern_ready = False     # will be true when a valid pattern is loaded

#^ get_cmd ====================================================================
#   Isolate alpha text from string. end when next char is non-apha  
#        Leave result in cmd_txt, return how many char in cmd_txt   
#
cmd_txt =""   # module variable
def get_cmd(txt):
#~ ============================================================================ 
    global cmd_txt
    scan    = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Need this to have JUST alpha char, no special char
    x       = len(txt)
    idx     = 0
    rv      = 0
    cmd_txt = ""
    while idx < x:
          data  = txt[idx]   # get a character from line
          data  = data.upper()  # make it upper case        
          alpha = scan.find(data)  # check for valid alpha character
          if alpha == -1:    # got a non-alpha char   
             x  = idx      # we are done
          else: 
            cmd_txt = cmd_txt + data     # build the command
            idx += 1   
    return len(cmd_txt)      

#^ check_command==============================================================
#                        Check a command line 
#  This function checks each command line and returns a proper return code
#  it ignores: 
#     blank lines
#     lines beginning with a comment (#) before a command 
valu          = 0       # a command variable
cmdvar        = 0       # an indicator if command has variables
command       = ""     # text of command mnemonic
def check_command(line):                                              
#~ ===========================================================================
    global cmd_table_idx
    command_char  = 0         # command char is actually a CMD_TABLE index
    rc            = error_func("NORMAL") # set default Return Code
    line2         = line.lstrip()           # strip off leading spaces (if any)
    index2        = line2.find("#")         # check for the beginning of a comment
    new_line      = line2.rstrip('\r\n')    # strip off ending CR/LF
    
    if globalv.debug is True: print("(004)",index2, len(new_line), new_line)

    if index2 != 0 and len(new_line) > 0:    # ignore line if comment at beginning of line or empty line
           #************************************
           #  EXTRACT THE COMMAND FROM LINE
           #************************************
       if globalv.debug is True:   print("(005) - should NOT get here on a comment...")
          
       cmd_len = get_cmd(line2)     # obtain the entire command, value returned is length of command
       if cmd_len == 0:    # got a "command"
          rc = error_func("INVALID_COMMAND")  # if no command found
       else:
          x              = line2[:cmd_len]  # extract command txt into temp string
          G.cmd_nmemonic = x.upper()        # convert temp into upper case and save it as a global variable
#          G.command      = G.cmd_nmemonic    # also save it as a local variable
          #**********************************
          #*  Check against table for a valid command
          #**********************************
          try:
             G.cmd_table_idx = CT.CMD_TABLE.index(G.cmd_nmemonic) # check to see if its in table
          except ValueError:
             G.cmd_table_idx = -1   # set not found
             
          if G.cmd_table_idx == -1:  # Found a valid command?
             rc = error_func("INVALID_COMMAND")  # No command found in table
          else:
             #****************************************************
             # CHECK IF ANY VARIABLES ARE ASSOCIATED WITH COMMAND
             # if so, process the variable
             #****************************************************
             G.cmd_no_xbyt = CT.CMD_TABLE[G.cmd_table_idx+4]   # save how many xtra byte for cmd
             if  G.cmd_no_xbyt != 0:    # check cmd_table if the command has a variable
                #******************************************************
                # VALIDATE VARIABLE AGAINST CMD_TABLE MIN/MAX VALUES
                #******************************************************
                     # extract the numeric value AFTER the alpha command
                vstring = line2[cmd_len:]  # get string AFTER command
                vstring = vstring.lstrip()   # strip off any blanks char after command (if any)
                x       = len(vstring)   # get the length of line after command
                nxt_idx = 0        # start looking here for numeric value
                while nxt_idx < x:     # keep getting characters until a non-digit or eol
                      data  = vstring[nxt_idx]   # get next character after command
                      if data.isdigit():          # scan line after command for numeric variable
                         nxt_idx+=1    # bump to next character on line
                      else:
                         x = nxt_idx   # we are done

                vnumb = vstring[:nxt_idx]   # attempt to extract the numeric variable from command line
                if globalv.debug is True: print("vnumb:",vnumb)
                   
                if len(vnumb) == 0:  # was a variable supplied??
                   rc = error_func("VARIABLE_EXPECTED")  # no, we were expecting a variable
                elif vnumb.isdigit() is False:  # test for non decimal values
                   rc = error_func("NON_NUMERIC_VALUE")  # only numeric variables are valid
                else:                  # Assume variable is present AND is numeric.
                   # ***************************************
                   # Now check numeric variable aginst mix/max values
                   # ***************************************
                   G.cmd_var = int(vnumb)   # make it a number to check against the min/max values in table
                   vmin = CT.CMD_TABLE[G.cmd_table_idx+2]   # check against the command table
                   vmax = CT.CMD_TABLE[G.cmd_table_idx+3]   # for valid numeric ranges
                   if G.cmd_var < vmin or G.cmd_var > vmax:    # are values within range?
                      rc = error_func("VALUE_OUT_OF_RANGE")             # NO - Set error
                   else:
                      #************************
                      #      BLOCK CHECKING
                      # Will check:
                      # 1. to see if block already exsists
                      # 2. check for nested blocks - trying to define a block when one is already being defined
                      #************************
                      if G.cmd_nmemonic == "BB":  # Are we defining a blocK?
                         block_no = G.cmd_var
                         if G.in_block != 0:           # yes - are we already in a block?
                            rc = error_func("NESTED_BLOCK")  # YES - cant define a block
                                                                #  when you are already in a block
                         else:
                            if G.block_table[block_no] != 0:   # has block alread been defined?
                               rc = error_func("BLOCK_ALREADY_DEFINED")  # yes, bad,bad
                            else:   
                               G.in_block = block_no         # no, indicate the block id beig defined

                      elif G.cmd_nmemonic == "EX":  # attemping to execute a block?
                           if G.in_block != 0:   # are we in a block definition?
                              rc = error_func("NO_BLOCK_EXECUTION_WITHIN_BLOCK_ALLOWED")  # yes - thats a no-no
                           else:
                              if G.block_table[G.cmd_var] == 0:   # has block been defined?
                                 rc = error_func("BLOCK_NOT_DEFINED")  # no - this is an error
                     
             #************************
             #    CHECK IF ENDING A BLOCK
             # if no block is open, this is an error, else just clear the in_block indicator
             #************************
             if G.cmd_nmemonic == "EB" and rc == NORMAL: # Ending a block
                if G.in_block == 0:  # YES - is the block open?
                   rc = error_func("NO_OPEN_BLOCK")  # no - this is an error
                else:                 
                   G.in_block = 0               # we are free to define another block
    else:
       if globalv.debug is True: print("(006) - Got a comment line...") 
       G.cmd_nmemonic = ""      # do not add commented lines
    return rc

#^ check_open_block ======================================================
#   this function is called when pattern file has reach End Of Filw (EOF)
#   it checks to see if a block definition was left not closed
def check_open_block():
#~ =======================================================================

    rc = NORMAL
    if G.in_block != 0:
       rc = error_func("BLOCK_LEFT_OPEN")  # if in_block != 0 - this is an error
    return rc   
           
#^ run_pattern ******************************************************************************
# * This function is called after the pattern file has been uploaded, encoded, and is correct  
# *
# * Pattern string is indexed by G.next_cmd_ptr 
# * Each cmd entry is an index into the CMD_TABLE and any associated values 
# * The CMD_TABLE is the key to running a pattern
# * Each command in the CMD_TABLE has a function associated with the command
# * ALL functions for a command are located in CMD_FUNCS.PY
# * this function references variables in globalv.py
def run_pattern(begin_idx): # typically begin at offset 0
#~ ***************************************************************************************
    G.nxt_pat_ptr = begin_idx     # Start pattern at begining
    p_len         = len(G.pattern)   # this is the end, dont go past this!
    G.nxt_pat_ptr = CT.CF.set_gvar(G.nxt_pat_ptr)  # get the command in pattern string (updates global variables)
                                                   # and returns the next pointer into pattern
    more = True
    while more and globalv.button_pressed is False:    # run the pattern ONCE
          if globalv.debug is True:
             print("Current command:", G.cmd_nmemonic,G.ivar,G.cmd_function,G.prv_pat_ptr,G.cur_pat_ptr,G.nxt_pat_ptr)
             # ********************************************
             # process the command
             # ********************************************
          if G.cmd_nmemonic != "RL":
             G.prv_pat_ptr  = G.cur_pat_ptr 
          elif G.cmd_nmemonic == "EB":
             G.prv_pat_ptr  = G.nxt_pat_ptr          

          if globalv.debug is True: print("After RL/EB check:",G.prv_pat_ptr,G.cur_pat_ptr,G.nxt_pat_ptr)    
                      
          G.nxt_pat_ptr  = G.cmd_function(G.ivar)  # do the function in cmd_func.py, include a variable, even if not used
              
#          if globalv.debug:
#             print("@272","cur:",G.cur_pat_ptr,"Nxt:",G.nxt_pat_ptr)
#             var2 = input("Paused......")
#          if globalv.debug:
#             print("at command:", G.cur_pat_ptr, G.cmd_nmemonic,G.ivar,G.cmd_function,G.cur_pat_ptr,G.nxt_pat_ptr)
#             print("Advancing to next cmd...")    

          if G.nxt_pat_ptr >= p_len: 
             more = False
          else:        # get the command in pattern string (updates global variables)       
             G.nxt_pat_ptr = CT.CF.set_gvar(G.nxt_pat_ptr)                                              
    return

#^ validate_line(line) ===========================================================
#   This function validate a command via check_command() function in cmd_pattern.py
#   if the line is valid, it builds the globalv.pattern string
#   this string is an encoded string of the pattern file made up of hex values.
#   Once the validation is complete and correct, it will run endlessly
def validate_line(line): 
#~ ===============================================================================
    global line_no
    rc       = NORMAL
    new_line = line.rstrip('\r\n')     # strip off ending CR/LF
    print(line_no, new_line)           # show the input line
    rc    = check_command(new_line)    # validate the command line
    if rc != NORMAL:   # Got an error
       error = error_func(rc)
       print("---------->",error, "on line",line_no)
       G.pattern = ""  # get rid of current pattern string  
    else:
       #************************
       #    COMMAND IS VALID, ATTEMPT TO ADD TO PATTERN LINE
       #************************
       if globalv.debug is True: print("(007) - Command valid....",G.cmd_nmemonic)
          
       if len(G.cmd_nmemonic) > 0:
          G.pattern = G.pattern + chr(G.cmd_table_idx)   # add at least, the command, to pattern string
          if G.cmd_no_xbyt == 1:
             G.pattern = G.pattern + chr(G.cmd_var)  # and any variables  

             if G.cmd_nmemonic == "BB":
                G.block_table[G.cmd_var] = len(G.pattern) # next byte in pattern string is where the block begins
                                                          # save this index into a block table indexed by block
          elif G.cmd_no_xbyt == 2:   # if 2 extra bytes, they are a 16bit int. that needs to be converted into two chars
               temp1 = G.cmd_var >> 8  # isolate high bits
               temp2 = G.cmd_var-(temp1 << 8) # isolate low bits              
               temp3 = chr(temp1) + chr(temp2) 
               G.pattern = G.pattern + temp3
    line_no += 1   
    return rc         
# G.pattern     = ""

# ---------------------------------- 204 msg ----------------------------------
def send_204():
    rc    = 0    # defaut Return Code
    resp = "HTTP/1.1 204 No Content\r\n"
    resp += "Connection: keep-alive\r\n"
    resp += "Allow: GET, POST, PUT, DELETE, OPTIONS\r\n"
    resp += "Access-Control-Allow-Origin: *\r\n"
    resp += "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n"
    resp += "Access-Control-Allow-Headers: Content-Type, Authorization\r\n"
    resp += "Access-Control-Max-Age: 86400\r\n"
    resp += "Content-Length: 0\r\n\r\n"
    WS.client.send(resp)
    return rc

# ------------------------------------------------------------------------------------------
# -------------- Send a web page (index.html) thag was loaded into memory ------------------
# ------------------------------------------------------------------------------------------
def send_root():

    if globalv.debug: print("Sending root page: ")
    
# ------ header info ALWAYS has an empty line in the header before Webpage contents 
# ------ Web page is already loaded into memory as wpage and its length as pagel both global variables
    WS.client.send('HTTP/1.1 200 OK\r\n')
    WS.client.send('Content-Type: text/html; charset=UTF-8\r\n')
    WS.client.send('Content-Length: ' + pagel + '\r\n\r\n')
    WS.client.send(wpage)

    return NORMAL 


# ---------------------------------- 200 msg --------------------------------
def send_200(txt):
    global resp
    rc    = 0    # defaut Return Code
    resp  = 'HTTP/1.1 200 OK\r\n'
    resp += 'Content-Type: text/html; charset=UTF-8\r\n'
    resp += 'Connection: keep-alive\r\n'
    resp += "Access-Control-Allow-Origin: *\r\n"    
    resp += 'Content-Length: ' + str(len(txt)) + '\r\n\r\n'
    resp += txt
    WS.client.send(resp)
    return rc

# --------------------------------- 200 w/close --------------------------
def send_200_close():
    txt  = "OK"
    resp  = 'HTTP/1.1 200 OK\r\n'
    resp += 'Content-Type: text/html; charset=UTF-8\r\n'
    resp += 'Connection: close\r\n'
    resp += "Access-Control-Allow-Origin: *\r\n"    
    resp += 'Content-Length: ' + str(len(txt)) + '\r\n\r\n'
    resp += txt
    WS.client.send(resp)
    
# ---------------------------------- 500 msg -------------------------------
def send_500():
    global resp
    resp  = 'HTTP/1.1 500 Internal Server Error\r\n'
    resp += 'Content-Type: text/plain; charset=UTF-8\r\n\r\n'
    resp += 'Error parsing JSON'
    WS.client.send(resp)
    return NORMAL

#^ handle_web ------------------------------------------------------------------------------
# This function handles the web communiction to the user
# It responds properly to web requests via standard web codes
# It waits for data from teh browser via the uPython recv function via the "try" mechanism
# The data is sent to the server via standard JSON objects
# 
def handle_web(conn):
#~ -----------------------------------------------------------------------------------------
    global line_no
    cpkt    = 0   # initialize packet count
    more    = True
    portal_request = True   # this is a flag if browswer asks for root page before we ask
    NORMAL  = error_func("NORMAL")
    rc      = NORMAL
    pattern_ready = False    # set this to False when table is being loaded
    while rc == NORMAL and globalv.button_pressed is False and more is True:
          try:                
             request = conn.recv(1024)   # receive data. Data will be formatted to utf-8

          except Exception as e:
                 print("Exception in handle_web:", e)
                 more = False
                 rc = error_func("UNDEFINED_ERROR")
#                 send_500()
          if globalv.debug is True: print("(001) Got data......",request)
          
          if not request:   # if no data obtained(len = 0), the connection was closed. stop pressinng
                 rc = error_func("BROWSER_CLOSED")
                   
          elif globalv.Robot_URL in request:   # only want to hear from our URL
               if globalv.debug is True: print("got proper host name")
                      
               request_str = request.decode('utf-8')
               parts       = request_str.split("\r\n\r\n")
               if "GET / " in request_str or "GET /index.html" in request_str:  # requesting root page
                  if globalv.debug: print("Requesting Root document")
                  
                  if "Connection: close" in request_str:
                     send_200_close()
                  else:   
                     send_root()           # no - send root document
                     line_no = 1           # set line # to 1 ater sending root page
                     
               elif "/favicon.ico" in request_str:
                    send_204() 
                     
               elif "OPTIONS /upload-line" in request_str:  # JSON options request
                    if globalv.debug: print("(003) Requesting OPTIONS response")
                    send_204()
                    
               elif len(parts) > 1:
                    if globalv.debug: print("(002) Parts: ",parts) 
                    body = parts[1]

                     # Parse JSON
                    data = json.loads(body)
                    txt  = data["line"]      # get line data
                    if len(txt) > 0 and "ETX" in txt:   # is browser done sending data?
                 # We need to either send "!ERROR" or "OK" msg
                 # if msg is error, we need t clear the pattern string and stay in loop
                 # if msg is "OK" set flag to run pattern and get out of this loop
                 # the running pattern MUST sense the globalv.button_pressed for a mode change
                       if globalv.debug is True: print("Browser is done sending")
                          
                       if G.in_block > 0:  # Are blocks still open??
                          error     = "! Block" + str(G.in_block) + " left open"
                          G.pattern = ""
                          if globalv.debug is True: print(error)
                             
                          send_200(error)   # yes - send back a reply
                       else:
                          pattern_ready = True 
                          send_200("Pattern File - OK")
                          more = False
                        #*******************************************
                        #   show pattern table being built
                        #*******************************************
                          if globalv.debug is True:   
                             rty= ":".join("{:02x}".format(ord(c)) for c in G.pattern)
                             print(len(G.pattern),"-",rty)
                    else:   
                       rc = validate_line(txt)      # ths is where the rcv'd command line gets checked
                       if rc != NORMAL:
                          error = "! " + error_func(rc)
                          print(error)
                          G.pattern = ""   # delete pattern string BC there is an error
                          more      = False   # get out of loop
                          send_200(error)   # send back the error command, we are done,
                       else:
                          send_200("OK")
                          #*******************************************
                          #   show pattern table being built
                          #*******************************************
                          if globalv.debug:
                             rty= ":".join("{:02x}".format(ord(c)) for c in G.pattern)
                             print(len(G.pattern),"-",rty)  
    WS.client.close()
    if globalv.debug is True:
       txt = error_func(rc)
       print("Return Code:",rc, "/",txt)
    return rc

# -------------------------
# Main loop
# -------------------------
def get_pattern():
    global conn, wpage, pagel, rc
    
    print("Entering Pattern mode")
    
    WS.start_server("ALL",UP)
    WS.set_poll_services()
    filenam = "pattern.html"
    with open(filenam,"r") as page:
         wpage   = page.read()
         pagel   = str(len(wpage))
         page.close()
         print("loaded",filenam, "\r\n")
         
    rc = NORMAL    
    while globalv.button_pressed is False and rc == NORMAL:
#          WS.get_web_connection()    # get a web connection and serve the page
          try:
             rc   = WS.get_web_connection()    # get a web connection and serve the page..
          except KeyboardInterrupt:
             print("\n **Keyboard interrupt received. Performing cleanup...")
             rc = error_func("KEYBOARD_INTERRUPT")
#             x = WS.shutdown_all_services()  # shut things own, dont care about return code
             break
          except Exception as e:
              print("Error:",e)
              break
                
    # Upon a sucessful tcp connection on port 80, the browser will send a GET request with a '/'
    # as the url. Typically the server will respond with the root document, which
    # is norally "index.html" which we will read into memory, then send
          if globalv.button_pressed is False and rc == NORMAL:
             WS.http_sock.setblocking(True)   # once we get a connection, never do a time out (Blocking)  
            
#             while globalv.button_pressed is False:   #  remote control mode....
             if globalv.debug is True:  print("going to handle the web...")
             G.clear_pattern()    # clear pattern data from memory
             pattern_ready = False   # signify that no pattern is in memory
             gc.collect()
             globalv.Platform.motor.drive(0,0)      # Make sure motors are stopped
             rc = handle_web(WS.client)     # handle the conversation from client
                                                # everything is handled there
             if rc == error_func("BROWSER_CLOSED") or rc == error_func("INVALID_COMMAND"):     # we come back here after hanling the web, many things can happen there
                                                       # browser closing is normal, we will wait for another connection here
                WS.client.close()      # close the connection
                gc.collect()              # collect garbage - python like to make garbage
#                if rc == error_func("BROWSER_CLOSED"):
                rc = NORMAL               # its ok forr browser to close
#                break         # get out of main loop
                      
             if rc != NORMAL:
                print(error_func(rc), rc)
             else:
                while globalv.button_pressed is False and rc == NORMAL and pattern_ready:
                      run_pattern(0)  # begin to run pattern at index 0

    if globalv.button_pressed is True:
       x = WS.start_server("ALL",DOWN)  # shut things down, dont care about return code
       G.clear_pattern()    # clear pattern data from memory   
       gc.collect()
    return rc                 # go back with a return code
