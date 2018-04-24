# DataServer1.py

from threading import Thread
import socket
import time
#import RPi.GPIO as GPIO
import sys

VERBOSE = True
IP_PORT = 12000
P_BUTTON = 24 # adapt to your wiring

def debug(text):
    if VERBOSE:
        print( "Debug:---", text)
        #blah

# ---------------------- class SocketHandler ------------------------
class SocketHandler(Thread):
    #def __init__(self, conn, motorController):
    def __init__(self, conn):
        Thread.__init__(self)
        self.conn = conn
        #self.motorController = motorController

    def run(self):
        global isConnected
        debug("SocketHandler started")
        while True:
            cmd = ""
            try:
                debug("Calling blocking conn.recv()")
                cmd = self.conn.recv(4096)
                cmdStr = str(cmd.decode())
            except:
                debug("exception in conn.recv()") 
                # happens when connection is reset from the peer
                break
            debug("Received cmd: " + cmdStr)
            if len(cmdStr) == 0:
                break
            self.executeCommand(cmdStr)
        self.conn.close()
        print ("Client disconnected. Waiting for next client...")
        isConnected = False
        debug("SocketHandler terminated")

    def executeCommand(self, cmd):

        ## --- for debug
        print("code gets here")
        print(cmd)

        debug("Calling executeCommand() with  cmd: " + cmd[0])
        
        if cmd == "F":
            print("F Recieved")
        elif cmd == "B":
            print("B Recieved")
        elif cmd == "L":
            print("L Recieved")
        elif cmd == "R":
            print("R Recieved")
        
        """
        
        if cmd[1] == "F":  # remove trailing "\0"
            if self.motorController.prev_command != cmd[1]:
                self.motorController.stop()
                self.motorController.goForward()
        elif cmd[1] == "B":
            if self.motorController.prev_command != cmd[1]:
                self.motorController.stop()
                self.motorController.goBackward()
        elif cmd[1] == "R":
            if self.motorController.prev_command != cmd[1]:
                self.motorController.stop()
                self.motorController.turnRight()
        elif cmd[1] == "L":
            if self.motorController.prev_command != cmd[1]:
                self.motorController.stop()
                self.motorController.turnLeft()
        elif cmd[1] == "S":
            if self.motorController.prev_command != cmd[1]:
                self.motorController.stop()
        elif cmd[1] == "C":
            if self.motorController.prev_command != cmd[1]:
                self.motorController.close()
        """

# ----------------- End of SocketHandler ----------------------
"""
class MotorController():
    def __init__(self, pwmR, fwdR, revR, pwmL, fwdL, revL):
        self.fwdR = fwdR
        self.revR = revR
        self.fwdL = fwdL
        self.revL = revL

        self.prev_command = ''
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pwmR, GPIO.OUT) # pwm Right
        GPIO.setup(fwdR, GPIO.OUT) # forward Right
        GPIO.setup(revR, GPIO.OUT) # reverse Right

        GPIO.setup(pwmL, GPIO.OUT) # pwm Left
        GPIO.setup(fwdL, GPIO.OUT) # forward Right
        GPIO.setup(revL, GPIO.OUT) # reverse Right

        GPIO.output(18,0)
        GPIO.output(23,0)
        GPIO.output(24,0)

        GPIO.output(19,0)
        GPIO.output(22,0)
        GPIO.output(27,0)

        self.pwmR = GPIO.PWM(pwmR,100)
        self.pwmL = GPIO.PWM(pwmL,100)

    def forwardRight(self, speed = 25):
        GPIO.output(23,0)
        GPIO.output(24,1)
        self.pwmR.start(speed)

    def backwardRight(self, speed = 25):
        GPIO.output(23,1)
        GPIO.output(24,0)
        self.pwmR.start(speed)
        
    def forwardLeft(self, speed=25):
        GPIO.output(22, 1)
        GPIO.output(27,0)
        self.pwmL.start(speed)

    def backwardLeft(self, speed=25):
        GPIO.output(22,0)
        GPIO.output(27,1)
        self.pwmL.start(speed)

    def goForward(self, speed = 25):
        self.forwardLeft(speed)
        self.forwardRight(speed)
        self.setPrevCommand("F")

    def goBackward(self, speed = 25):
        self.backwardLeft(speed)
        self.backwardRight(speed)
        self.setPrevCommand("B")

    def turnLeft(self, speed = 25):
        self.forwardRight(speed)
        self.backwardLeft(speed)
        self.setPrevCommand("R")

    def turnRight(self, speed = 25):
        self.forwardLeft(speed)
        self.backwardRight(speed)
        self.setPrevCommand("L")

    def stopLeft(self):
        self.pwmL.stop()
        
    def stopRight(self):
        self.pwmR.stop()
        
    def stop(self):
        self.stopLeft()
        self.stopRight()
        self.setPrevCommand("S")

    def close(self):
        self.stop()
        GPIO.cleanup()
        
    def setPrevCommand(self,prev_command):
        self.prev_command = prev_command
"""

def main(args):
      
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # close port when process exits:
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    debug("Socket created")
    HOSTNAME = "" # Symbolic name meaning all available interfaces
    try:
        serverSocket.bind((HOSTNAME, IP_PORT))
    except socket.error as msg:
        print ("Bind failed", msg[0], msg[1])
        sys.exit()
    serverSocket.listen(10)

    print ("Waiting for a connecting client...")
    isConnected = False

    while True:
        debug("Calling blocking accept()...")
        conn, addr = serverSocket.accept()
        #motorController = MotorController(18,23,24,19,22,27)
        print ("Connected with client at " + addr[0])
        isConnected = True
        #socketHandler = SocketHandler(conn, motorController)
        # necessary to terminate it at program termination:
        #socketHandler.setDaemon(True)
        #socketHandler.start()

        ## ---- for debug purposes -------##
        socketHandler = SocketHandler(conn)
        socketHandler.setDaemon(True)
        socketHandler.start()



        t = 0
        while isConnected:
            # necessary to terminate it at program termination:
            x = 0
        conn.close()
        GPIO.cleanup()
        


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
