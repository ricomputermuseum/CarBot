#^ REMOTE.PY ************************************************************************
# *                      Remote control via web browser
# * Version: 1.0
# * Date:    4/12/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
# *
# * Logic: Starts a WiFi accees point with SSID specified in globalv module
# *        Password is same as SSID
# *        Starts a Web server on Port 80. Only 1 client connection allowed
# *        Stats a DNS server to allow "RICM.XXX" to be used as URL
# *        Once a browser connects, it will display a joystick type of interface
# *
# * Entry Point:   RemoteMode(motor):   (motor driver instance)
# *
# * Check return_codes.py for all available return codes from this module
# * Dependants: network
# *             socket
# *             globalv
# *             web_stuff
# *             gc
# *             return_codes
#~ **********************************************************************************
import network          # standard Micropython
import socket           # standard Micropython
import globalv          # Global variables
import web_stuff as WS  # ap, ns & web stuff
import gc               # standard micropyton for garbage collection
import return_codes as RC    # obtain RICM return codes

rc   = RC.NORMAL      # Initialize default global return code

UP   = True
DOWN = False

def inet_aton(addr):   # takes a ip addr "x.x.x.x" and turns it into a binary format, tuple
    return bytes(map(int, addr.split(".")))
   
#^ send_root -----------------------------------------------------
# Send the web page that was loaded into memory (wpage)
#
def send_root(conn):
#~ ---------------------------------------------------------------
    if globalv.debug:
       print("Sending root page: ")
    
# ------ header info ALWAYS has an empty line in the header before Webpage contents 
# ------ Web page is already loaded into memory as wpage and its length as pagel both global variables
    conn.send('HTTP/1.1 200 OK\r\n')
    conn.send('Content-Type: text/html; charset=UTF-8\r\n')
    conn.send('Content-Length: ' + pagel + '\r\n')
    conn.send("Connection: keep-alive\r\n\r\n")
    conn.send(wpage)

    return RC.NORMAL 

#^ send_200_rname -------------------------------------------    
# Send robot name to browser
# Robot name is located in globalv.py
def send_200_rname(conn):
#~ ----------------------------------------------------------
    msg     = globalv.Robot_Name
    
    conn.send('HTTP/1.1 200 OK\r\n')
    conn.send('Content-Type: text/html; charset=UTF-8\r\n')
    conn.send('Content-Length: ' + str(len(msg)) + '\r\n\r\n')   # note empty line... needed
    conn.send(msg)
        
    return RC.NORMAL

#^ Send_204 ------------------------------------------------------    
#  Send a NO Content reply 204 to browser
#  Keep the connection alive
#
def send_204(conn):
#~ ----------------------------------------------------------------
    resp = "HTTP/1.1 204 No Content\r\n"
    resp += "Connection: keep-alive\r\n\r\n"
    conn.send(resp.encode('utf-8'))
    
    return RC.NORMAL
    
#^ Send_200_ok_close ---------------------------------------------
# Send a 200 msg to bowser and close the connection
#
def send_200_ok_close(conn):
#~ ---------------------------------------------------------------
    response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
                "<html><body><h1>Final web page</h1>"
                "<p>Connected successfully to your device! and connection closing</p></body></html>"
                )
    conn.send(response)
    return RC.NORMAL
    
#^ send_404 ------------------------------------------------------
# Send a 404 (page not found) to browser
def send_404(conn):
#~ ---------------------------------------------------------------
    response = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n"
    conn.send(response)
    return RC.NORMAL
    
#^ handle_client -------------------------------------------------
#                      Handle web page conversation 
# This is the main web handeling routine. 
# it stays in this routine until the user closes the browser, or mode is changed
#
def handle_client(conn,motor): 
#~ ------------------------------------------------------------------------ 
    cpkt    = 0   # initialize packet count
    if globalv.debug is True:
       print("----------------At handle_client:-----------------------")
       print(conn)
    
    rc      = RC.NORMAL    
    while rc == RC.NORMAL:
          try:                
             request_str = conn.recv(1024).decode('utf-8')   # receive data. Data will be formatted to utf-8
          
          except OSError as ERR:
                 rc = RC.SOCKET_ERROR        # OS error - return as socket error
                 if globalv.debug:
                    print(f"OS Error: {ERR}")
                    print(f"Socket_Conn: {conn}")
                 break
          except Exception as e:
                 rc = RC.UNDEFINED
                 if globalv.debug:
                    print("Try Error in handle_client:", e)
                 break
                      
          if globalv.debug is True:
             print("--------------------After recv:----------------------------")
             print(request_str)
             print("-----------------------------------------------------------")
                
          if not request_str:   # if no data obtained(len = 0), the connection was closed. stop pressinng
                rc = RC.BROWSER_CLOSED    # yes - Then user closed browser, else do nothing
                
          if rc == RC.NORMAL:
             if "GET / " in request_str or "GET /index.html" in request_str:  # requesting root page
                if globalv.debug:
                   print("--------------Requesting Root document")
                      
                if "Connection: close" in request_str:
                   send_200_ok_close(conn)
                else:   
                   send_root(conn)           # yes - send it                            
             elif "/move?" in request_str:         # see if the words "/move" are in the response
                  send_204(conn)  # send back a completed msg 
                  query  = request_str.split(" ")[1]
                  params = query.split("?")[1]
                  pairs  = params.split("&")
                  data   = {k: int(v) for k, v in (p.split("=") for p in pairs)}
                  ix     = data.get("x", 0)
                  iy     = data.get("y", 0)
                  rpk    = data.get("p", 0)  # received packet #
           
                  if rpk != cpkt:       # is calculated packet same as received packet
                     if globalv.debug: 
                        print("Pkt expected:",cpkt,"Rvd:", rpk)  # no - show difference
                     cpkt = rpk    # then make the same
                  cpkt += 1     # update packet count
                  Diff     = ix*10 
                  Throttle = iy*10
                  if globalv.debug:
                     print("Sending to driver: ", Diff,Throttle,cpkt-1)
                  
                  rc = motor.drive(Diff,Throttle)  # Drive the wheels  
                                                   # RC is an indicator that wheels were driven ok

             elif "/rname?" in request_str:         # robot name is being requested
                  if globalv.debug: 
                     print("Requesting robotname") 
                  send_200_rname(conn)
             else:
                  send_204(conn)   # Anything else was sent, just ignore it

             if globalv.button_pressed is True:        # check if butto was pressed
                rc = RC.MODE_CHANGE                    # tes - set Return code, and terminate While loop
                   
    if globalv.debug is True:
       print("Return Code from handle_client():",rc)
#    x = input("Paused before return......")
    return rc
  
#^ RemoteMode ****************************************************
# *                   WEB remote control                         
# * This is called by MAIN.PY when new_mode = REMOTE.
# * 
# * This function will wait for a browser connection and once a
# * connection has been made, it will call the HANDLE_CLIENT
# * function in this module to process all the user interaction. 
# * The user interface is a simple joystick control, which is very 
# * intuitive. 
# * All functions return with a return code. A 0 return code means
# * a function was sucessful, and negative number means some sort
# * of an error, a positive number means, function returned a value
# * that may need further processing. All return codes are in the 
# * RETURN_CODES.PY module.
# * This module constantly checks GLOBALV.BUTTON_PRESSED to
# * determine if the user wants to change a mode. When this happens
# * ALL Web services are terminated, memory is reclaimed, and
# * it returns to the MAIN.PY with a return code           
# *                                                              
def RemoteMode(motor):
#~ ***************************************************************
    global conn, wpage, pagel, rc
    
    setup = True                     # We are in setup. if the new mode changes,
                                     #     while we are in setup, we need to abort setup
    page2load = "remote.html"                                 
    print("Entering REMOTE mode.")
    abort = False
    ds = 0   
# load web page into memory 
    with open(page2load,"r") as page:  # read web page into memoryimport uos
         wpage   = page.read()
         pagel   = str(len(wpage))
         page.close()
         print("loaded", page2load, "page.\r\n")
         
    rc = WS.start_server("ALL",UP)
    rc = WS.set_poll_services()            # begin to poll servers (DNS & HTTP)   
   
    connection = False
# Wait until we get a web connection from user or button is pressed to change mode
    while globalv.button_pressed is False and rc == RC.NORMAL:
          try:
             rc = WS.get_web_connection()    # get a web connection and serve the page..
             connection = True
             if globalv.debug:
                print("in Remote - got a web connection") 
          except KeyboardInterrupt:
             print("\n **Keyboard interrupt received. Performing cleanup...")
             rc    = RC.KB_INTERRUPT
             break
          except Exception as e:
              print("Error:",e)
                
    # Upon a sucessful tcp connection on port 80, the browser will send a GET request with a '/'
    # as the url. Typically the server will respond with the root document, which
    # is normally "index.html" which has been read into memory, then send
          if globalv.button_pressed is False and rc == RC.NORMAL and connection is True:
#             WS.client.setblocking(True)   # once we get a connection, never do a time out (Blocking)  
       
             if globalv.debug:
                print("In remote after getting an HTTP connection:",WS.conn)
          
             while globalv.button_pressed is False and rc == RC.NORMAL:   #  remote control mode....
                   rc = handle_client(WS.client,motor)     # handle the conversation from client
                                                           # everything is handled there
                   if rc != RC.NORMAL:
                      if rc == RC.BROWSER_CLOSED or rc == RC.SOCKET_ERROR:
                         print("Browser Terminated connection.", rc)     # this is ok, handle it here
                         x = WS.client.close()
                         gc.collect()                    # collect garbage
                         connection = False 
                         motor.drive(0,0)     # make sure motors are off
                         rc = RC.NORMAL       # this is normal for broswer to close connection, get another conneciton
                         break
                      else:   
                         print("Error in handle_client function. RC:",rc)
                         
    motor.drive(0,0)          # make sure motors are off
    WS.start_server("ALL",DOWN)  
    return rc                 # go back with a return code
