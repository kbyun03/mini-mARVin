# DataClient1.py

from threading import Thread
import socket, time

VERBOSE = True
IP_ADDRESS = "143.215.102.135"
IP_PORT = 12000

def debug(text):
    if VERBOSE:
        print ("Debug:---", text)

def sendCommand(cmd):
    debug("sendCommand() with cmd = " + cmd)
    try:
        # append \0 as end-of-message indicator
        eol = "\0"
        sock.sendall(cmd.encode())
    except socket.error as msg:
        debug("Exception in sendCommand()" + msg[:])
        closeConnection()

def closeConnection():
    global isConnected
    debug("Closing socket")
    sock.close()
    isConnected = False

def connect():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    debug("Connecting...")
    try:
        sock.connect((IP_ADDRESS, IP_PORT))
    except:
        debug("Connection failed.")
        return False
    return True

sock = None
isConnected = False

if connect():
    isConnected = True
    print ("Connection established")
    time.sleep(1)
    while isConnected:
        cmd = input("Enter a command: ")
        sendCommand(cmd)
else:
    print ("Connection to %s:%d failed" % (IP_ADDRESS, IP_PORT))
print ("done")
