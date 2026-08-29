#^ WEB_STUFF.py *********************************************************************
# * Contains GLOBAL VALUES across all modules
# *
# * Version: 1.0
# * Date:    3/20/2026
# * By:      Ray Young
# * For:     Rhode Island Computer Museum (RICM)
# *
# * This module handles all internet & web servers. The system is setup as an access
# * point server. It also sets up a DNS server so that all DNS requests wll point
# * to the default IP Addr set in AP_IP. 
# * A simple web server is also implimented. It only responds to HTTP and not HTTPS
# * HTTPS is a bear to impliment on a PICO due to sooooo many different methods 
# * that various browsers use. The PICO also has limited resources, and in micropython,
# * is not full featured.
# * The time settings must be accurate as well to ensure certs keep working.
# * I tried to impliment a simple DNS server to handle DNS requests, but most 
# * browswer want to use HTTPS. If a domain name ends with  .com, .net, .org or other 
# * such popular domains, a webserver willl want to use HTTPS. the answer was to use
# * a .run domain. with HTTPS, Security certificates must be periodically updated, 
# * some browsers complain about self-generated certificates as well
#~ **********************************************************************************
import machine
import globalv
import network
import time
import socket
import select
import return_codes as RC

# ------------------ MODULE GLOBAL VARIABLES ------------
AP_IP   = "192.168.4.1"   # default IP addr
SUBNET  = "255.255.255.0"
GATEWAY = AP_IP   # this does not matter, as we are NOT connected to the internet
DNS     = AP_IP   # this is iportant so we can intercept the DNS request
wpage   = ""      # actual web page
pagel   = 0       # web pagel length make sure its UNDER 6k!
conn    = None    # placeholders for conn & addr
addr    = None
UP      = True
DOWN    = False

# ---------------------- DO NOT USE .com, .net, .org in globalv.py as browswers assume that its https!

#^ set_dns_response ----------------------------------------------
# DNS RESPONSE
# This function will format a standard response to re-direct to our AP_IP
# It requires the DNS Query to extract headers & other information for
# The correct response will be returned on exit
#
#~ ---------------------------------------------------------------
ip_bytes = bytes(map(int, AP_IP.split(".")))

def set_dns_response(query):   # this is our response to a DNS request. it always points to the address of the PICO

    transaction_id = query[:2]

    flags      = b'\x81\x80'
    questions  = b'\x00\x01'
    answers    = b'\x00\x01'
    authority  = b'\x00\x00'
    additional = b'\x00\x00'

    header = (
        transaction_id +
        flags +
        questions +
        answers +
        authority +
        additional
    )

    idx = 12

    while query[idx] != 0:
        idx += 1

    question = query[12:idx + 5]

    answer = (
        b'\xc0\x0c'
        b'\x00\x01'
        b'\x00\x01'
        b'\x00\x00\x00\x3c'
        b'\x00\x04' +
        ip_bytes
    )

    return header + question + answer

#^ start_server --------------------------------------------------
# This function is responsible for starting/stopping services 
# such as "AP", "DNS", "HTTP" with either "UP" or "DOWN"
# UP is a logical True, DOWN is a logical False
#
def start_server(serv_name,up):
#~ ---------------------------------------------------------------
    global ap,dns_sock,http_sock
    if serv_name == "AP" or serv_name == "ALL":
       if up is True: 
          print("Wait for WiFi to stabilize..")   # recomended from Raspberry
          time.sleep(1.5)    # add this to allow the wifi chip to power up
          ap = network.WLAN(network.AP_IF)
          ap.ifconfig((AP_IP, SUBNET, GATEWAY, DNS))  # assign Ip addr, Subnet, Gateway & DNS
          ap.config(essid=globalv.Robot_Name,password=globalv.Robot_Passwd)  # set WiFi name & password
          ap.config(pm=ap.PM_NONE)   # Turn off power managment
          ap.active(True)            # Turn it on

          while not ap.active():
                time.sleep_ms(100)  # wait to become active
    
          time.sleep(3)      # wait for WiFi to be on the air....
          print("AP Active...\r\n")    # READY!
       else:
          ap.active(False)     # shutdown AP
          ap.deinit()          # De-initialize AP
          print("AP Shutdown.")
 
# *********************************************************
# *          SETUP DNS & HTTP SOCKETS                     *
# *********************************************************
#                  DNS UDP 53      
    if serv_name == "DNS" or serv_name == "ALL":
       if up is True: 
          dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          dns_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          dns_sock.bind(("0.0.0.0", 53))

          print("DNS Active...\r\n")
       else:
          dns_sock.close()
          print("DNS Shutdown.")
    
#                HTTP TCP 80
    if serv_name == "HTTP" or serv_name == "ALL":
       if up is True: 
          addr      = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
          http_sock = socket.socket()
          http_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          http_sock.bind(addr)
          http_sock.listen(1)

          print("HTTP Server Active..\r\nWaiting for web connection...\r\n")
       else:
          http_sock.close()
          print("HTTP Server shutdown.")
    return RC.NORMAL

#^ set_poll_services ---------------------------------------------
# This function will set up polling services for DNS & HTTP
# requests. it handles TCP socket connections by pollint them
# istead of waiting on each one independently.
#
def set_poll_services():
#~ ---------------------------------------------------------------
    global poller
# *********************************************************
# *                   SETUP a POLLER                      *
# *********************************************************
    poller = select.poll()

    poller.register(dns_sock, select.POLLIN)
    poller.register(http_sock, select.POLLIN)
    return RC.NORMAL

#^ get_web_connection() --------------------------------------------
#  Stay in loop waiting for either DNS requests, or HTTP requests....  
# 
def get_web_connection():
#~ -----------------------------------------------------------------
    global poller,client,addr      # make these vaiables public     

    rc   = RC.NORMAL
    more = True
    while globalv.button_pressed is False and more is True:
          events = poller.poll(1000)   # loop thru events every 1,000ms or every second
          for sock, event in events:

              if sock == dns_sock:
              # *************************************************
              # *               HANDLE DNS QUERY                *
              # *************************************************
                 try:
                    data, addr = dns_sock.recvfrom(512)
                    idx = 12 
                    while data[idx] != 0:
                          idx += 1
                    url = data[12:idx]      # extract URL from DNS Query
                    qtype = data[idx+2]     # get query type

                    if url == globalv.wurl and qtype == 1:     # only answer for robot.run and query type = 1....
                       response = set_dns_response(data)
                       dns_sock.sendto(response, addr)
                       if globalv.debug is True:
                          print("Sent DNS URL:", data)
                       
                 except Exception as e:
                        print("EXCEPTION!! DNS error:", e)

              elif sock == http_sock:
              # *************************************************
              # *         HANDLE HTTP REQUEST                   *
              # *************************************************
                   if globalv.debug is True:
                      print("Got an HTTP connection request..........")
                   client, addr = http_sock.accept()    # accept returns a socket object (conn) for each client
                   if globalv.debug:
                      print("Client:",client)
                      print("Addr:",addr)
                   rc   = RC.NORMAL
                   more = False     # have a connection, go back to caller with a valid connection 
    return rc 
                                             
#^ shutdown_all_services -------------
#     Terminate all services
# 
def shutdown_all_services():
#~ -----------------------------------
    global web_valid
    
    print("Terminating services")
    start_server("ALL",DOWN)
    web_valid = False    # we must re-validate thru DNS
    
    return
