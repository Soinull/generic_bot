#!/usr/bin/env python
#Generic bot code
#Author- Tim Crothers
#Sep 2015
#Rev 1.5

import socket
import os
import re
import thread
import threading
import time
import datetime

bufsize    = 1024
port       = 29876
server     = '172.16.89.129'
botname    = 'generic_bot'
botpass    = 'pass'

bot_responses = dict()                                  # The bot_responses is for canned responses to commands that don't require actual work
bot_responses['GETLOCALIP'] = "My IP: 192.168.1.42"               # Useful for "faking" real responses to mimic the actual bot being portrayed
bot_responses['test2'] = "second test received"

# #################################################################
#
#  Classes "Operation & Manager" set up the timer functionality
#
# #################################################################

class Operation(threading._Timer):
    def __init__(self, *args, **kwargs):
        threading._Timer.__init__(self, *args, **kwargs)
        self.setDaemon(True)

    def run(self):
        while True:
            self.finished.clear()
            self.finished.wait(self.interval)
            if not self.finished.isSet():
                self.function(*self.args, **self.kwargs)
            else:
                return
            self.finished.set()

class Manager(object):

    ops = []

    def add_operation(self, operation, interval, args=[], kwargs={}):
        op = Operation(interval, operation, args, kwargs)
        self.ops.append(op)
        thread.start_new_thread(op.run, ())

    def stop(self):
        for op in self.ops:
            op.cancel()

# #################################################################
#
#  These modules mimid various actual bot functionality
#
# #################################################################

def keepalive():                                # This is the functional called every xx to send a keepalive (ping in this bot case)
    global f, srvsock
    xmit=srvsock.sendall("PING\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+"PING\n")

def xmit_garble(cleartext,garbletext):          # Placeholder function - Actual "encryption" should go here as dictated by the bot being mimicked
    garbletext = cleartext
    
def xmit_ungarble(garbletext,cleartext):        # Placeholder function as above
    cleartext = garbletext
    
def ping():                                     # Respond to a ping with a pong
    global f, srvsock
    xmit=srvsock.sendall("PONG!\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+"PONG!\n")
    
def udpflood(cmd):                                 # Bot told to do a UDP flood
    global f, srvsock
    target = cmd.split(' ')
    xmit=srvsock.sendall("UDP Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+"UDP Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")

def tcpflood(cmd):                                 # Bot told to do a TDP flood
    global f, srvsock
    target = cmd.split(' ')
    xmit=srvsock.sendall("TCP Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+"TCP Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")

def junk(cmd):                                     # Bot told to do a junk DoS flood
    global f, srvsock
    target = cmd.split(' ')
    xmit=srvsock.sendall("JUNK Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+"JUNK Flooding "+target[1]+":"+target[2]+" for "+target[3]+" seconds\n")
    
def logoff():                                   # Shutdown bot as requested - too suspicious to stay otherwise
    global f, srvsock, timer
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"< "+"## Told to shutdown ##\n")
    timer.stop()
    srvsock.close()
    f.close()
    exit()
    
# #################################################################
#
#  Main bot loop
#
# #################################################################

def Main():
    global f, srvsock, bot_responses, timer

    f = open('bot.log','a')
    f.write('###############################################\n')
    f.write('##    Connecting to C2 '+server+'\n')
    f.write('##    '+datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S UTC")+'\n')
    f.write('###############################################\n\n')

    srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvsock.connect((server, port))
    
    timer=Manager()
    timer.add_operation(keepalive,30)           # This sets up a timer that calls the keepalive function every 30 seconds - timing as per bot emulated

    pattern1 = '.*:(\w+)\W*%s\W*$' % (botname)  # Parsing for commands directed to the bot in a couple different ways
    pattern2 = '.*:%s\W*(\w+)\W*$' % (botname)

#    while 1:                                    # Most bot channels will require authentication of some sort - Gafgyt doesn't
#        srvmsg = srvsock.recv(bufsize).strip()
#        if srvmsg.find("identity") != -1:
#            xmit=srvsock.sendall(botname+"\n")  # Replace identity with the appropriate login prompt used by the C&C
#        elif srvmsg.find("password") != -1:
#            xmit=srvsock.sendall(botpass+"\n")  # Replace password with the appropriate password prompt used by the C&C
#        else:
#            break

    # The next line announces the bot in the channel as it joins
    
    xmit=srvsock.sendall("Linux antares 3.13.0-35-generic #62-Ubuntu SMP "+datetime.datetime.now().strftime("%a %b %d %I:%M:%S CDT %Y")+" i686 athlon i686 GNU/Linux.\n")
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S")+"> "+"Linux antares 3.13.0-35-generic #62-Ubuntu SMP "+datetime.datetime.now().strftime("%a %b %d %I:%M:%S CDT %Y")+" i686 athlon i686 GNU/Linux.\n")

    while 1:
        srvmsg = srvsock.recv(bufsize).strip('\r\n')
        f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"< "+srvmsg+"\n")

        try:
            if srvmsg.index('*') != 0:
                srvmsg = srvmsg[3:len(srvmsg)]                 # This is just to strip off some leading characters particular to the server
        except:
            srvmsg=srvmsg
            
        print srvmsg

        m1 = re.match(pattern1, srvmsg, re.I)
        m2 = re.match(pattern2, srvmsg, re.I)
        if ((m1 == None) and (m2 != None)): m1 = m2
    
        if (m1 != None):
            word = m1.group (1)
            word = word.lower()
        else:
            word = srvmsg
#            try:
#                word = srvmsg[srvmsg.index(':')+1:]     # Delimiter (if any) in the Bot channel
#            except:
#                word = ''

#        word = word.lower().strip()

        if (word in bot_responses):
            xmit = srvsock.sendall(bot_responses[word]+"\n")
            f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"> "+bot_responses[word]+"\n")

        if srvmsg.find("PING") != -1:                   # Recieved a ping request - better respond
            ping()

        if srvmsg.find("UDP") != -1:                    # Received a UDP flood command
            udpflood(srvmsg)
            
        if srvmsg.find("TCP") != -1:                    # Received a TCP flood command
            tcpflood(srvmsg)
            
        if srvmsg.find("JUNK") != -1:                   # Received a junk flood command
            junk(srvmsg)
                        
        if srvmsg.find("LOLNOGTFO") != -1:              # Received a shutdown request
            logoff()
try:            
    Main()
except KeyboardInterrupt:
    f.write(datetime.datetime.utcnow().strftime("%Y-%m-%d %I:%M:%S ")+"< "+"## ^C Received from console ##\n")
    timer.stop()
    srvsock.close()
    f.close()
    exit()

