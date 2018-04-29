#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gpiozero.output_devices import PWMOutputDevice, DigitalOutputDevice
from gpiozero.devices import GPIODevice, Device, CompositeDevice
from gpiozero.threads import GPIOThread
from gpiozero.mixins import SourceMixin
from sonarDist import DistanceSensor
from threading import Lock, Thread
import socket
import time
import sys
from imuHeading import ImuPosHeading
import serial
from math import cos, sin

VERBOSE = True

global initialHeading
global sockConn
global imuObj
global pwm
global sonarObj


def debug(text):
    if VERBOSE:
        print( "Debug:---", text)



class SocketConnect():
    def __init__(self,port=12000):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.host = ''
        self.port = port;

        try:
            self.socket.bind((self.host,self.port))
        except socket.error as msg:
            debug('Bind failed', msg[0], msg[1])
            sys.exit()
        self.connected = False
        self.openConnection = False
        self.quit = False
        self.sendMessage = ''
        self.socket.listen(10)
        self.messageType = {0:'MARV', 1:'OBST', 2:'HEAD'}
        debug('listening...')
        self.tConn = Thread(name = 'conn', target = self.checkConnection)
        self.tSend = Thread(name = 'send', target = self.socketSender)
        self.tRecv = Thread(name = 'recv', target = self.socketReciever)
        self.mutex = Lock()
        self.tConn.start()

    def addToSendMessage(self, msg, a_type):
        '''
            msg is data as a string of x,y coord
            type is either 0 for marvin loc or 1 for obstacle loc; 2 is heading

            message types will be delineated by ';', data values (such as diff obstacle locations)
            will be delineated by ' '

         '''
        self.sendMessage = self.sendMessage + self.messageType[a_type] + ' ' + msg + ' ' + '; '

    def checkConnection(self):
        while (1):
            self.mutex.acquire()
            if (not self.connected) and (not self.openConnection):
                self.conn, self.addr = self.socket.accept()
                debug('connected')
                self.connected = True
                self.openConnection = True
                self.mutex.release()
                self.tSend.start()
                self.tRecv.start()
                self.motorR = MotorR()
                self.motorL = MotorL()
            elif (not self.connected) and (self.openConnection):
                self.closeConn()
                self.openConnection = False
                self.mutex.release()
        
            if self.quit:
                if self.openConnection or self.connected:
                    self.closeConn()
                    self.openConnection = False
                self.mutex.release()
                break

    def socketSender(self):

       while(1):
           try:

                if len(self.sendMessage) is not 0:
                   debug('sending: ' + self.sendMessage)
                   self.conn.sendall(self.sendMessage.encode())
                   self.sendMessage = ''

           except socket.error as eMsg:
               debug('exception occured in conn.sendall():' + str(eMsg))
               self.connected = False

    def socketReciever(self):
        while (1):
            cmd = ''
            try:
                cmd = self.conn.recv(4096)
                cmdStr = str(cmd.decode())
                debug('recieved command: ' + cmdStr)
            except socket.error as msg:
                debug('exception in conn.recv():' + str(msg))
                self.connected = False
                break

            if len(cmdStr) == 0:
                self.connected = False
                break

            self.executeCommand(cmdStr)

    def closeConn(self):
        try:
            self.tSend.join()
            self.tRecv.join()
            self.conn.close()
        except:
            debug('error closing connection')

    def executeCommand(self,cmd):
        if cmd == 'F':
            debug('cmd==f')
            self.motorL.stop()
            self.motorR.stop()
            time.sleep(0.1)
            self.motorL.forward(0.5)
            self.motorR.forward(0.45)
        elif cmd == 'B':
            self.motorL.stop()
            self.motorR.stop()
            time.sleep(0.1)
            self.motorL.backward(0.45)
            self.motorR.backward(0.5)
        elif cmd == 'R':
            self.motorL.stop()
            self.motorR.stop()
            time.sleep(0.1)
            self.motorL.forward(0.5)
            self.motorR.backward(0.5)
        elif cmd == 'L':
            self.motorL.backward(0.5)
            self.motorR.forward(0.5)
        elif cmd == 'S':

            self.motorL.stop()
            self.motorR.stop()

            imuObj.reInit()
            heading = imuObj.readIMU(initialHeading)
            print ("Heading %5.2f" % (heading))
            xyMarv = sonarObj.collectAngleVectors(heading)
            xyMarvString = '[' + str(xyMarv[0]) + ',' + str(xyMarv[1]) + ']'
            print ("Marvin " + xyMarvString)

            d = sonarObj.readSonar()

            print ('Sonar Dist Data: ' + str(d))

            
##            obstLocString = sonarObj.getObstacleLoc(heading)
##            print ("Obstacal Location " + obstLocString)
            sockConn.addToSendMessage(str(heading), 2)
            sockConn.addToSendMessage(xyMarvString, 0)
##            sockConn.addToSendMessage(obstLocString, 1)





class Sonar():
    def __init__(self):
        self.sonarSensors = { 'front': 0, 'back': 1, 'left': 2, 'right':3}

        self.sonarDistObj = DistanceSensor()

    def readSonar(self): 
        ''' adds distance read to distance list; dist is in m '''

        return self.sonarDistObj.distance


   
    # oops this is for lidar
    def adjustAngle(self,angle):
        DutyCycle  = 1.0/18*(angle)+2.2;
        return DutyCycle

    # also for lidar.. obviously
    def readLiDAR(self):

        ser = serial.Serial('/dev/ttyUSB0',115200,timeout = 1)

        #ser.write(0x42)
        ser.write(bytes(b'B'))

        #ser.write(0x57)
        ser.write(bytes(b'W'))

        #ser.write(0x02)
        ser.write(bytes(2))

        #ser.write(0x00)
        ser.write(bytes(0))

        #ser.write(0x00)
        ser.write(bytes(0))

        #ser.write(0x00)
        ser.write(bytes(0))

        #ser.write(0x01)
        ser.write(bytes(1))

        #ser.write(0x06)
        ser.write(bytes(6))

        Dist_Total = 0;
        counter = 0;

        while(True):
            while(ser.in_waiting >= 9):
                if((b'Y' == ser.read()) and ( b'Y' == ser.read())):

                    Dist_L = ser.read()
                    Dist_H = ser.read()
                    Dist_Total = (ord(Dist_H) * 256) + (ord(Dist_L))
                    for i in range (0,5):
                        ser.read()
                    if(counter==20):
                        return Dist_Total
                    counter = counter+1

    def collectAngleVectors(self,heading):
        y = 0
        x = 0
        maxY = 143
        maxX = 77
        coordinates = []
        global pwm
        if heading <=0 and heading > -45:
            #Collect Data from Walls 4 and 1
            pwm.value = self.adjustAngle(90+heading)/100
            time.sleep(.5)
            x = maxX- self.readLiDAR()
            pwm.value = self.adjustAngle(180+heading)/100
            time.sleep(.5)
            y = self.readLiDAR()

        if heading <= -45 and heading > -90:
            #Collect Data from Walls 4 and 1
            pwm.value = self.adjustAngle(90+heading)/100
            time.sleep(.5)
            x = maxX- self.readLiDAR()
            pwm.value = (self.adjustAngle(180+heading))/100
            time.sleep(.5)
            y = self.readLiDAR()

        if heading <=-90 and heading >-135:
            #Collect Data from Walls 2 and 1
            pwm.value = self.adjustAngle(180+heading+90)/100
            time.sleep(.5)
            x = self.readLiDAR()
            pwm.value = self.adjustAngle(90+heading+90)/100
            time.sleep(.5)
            y = self.readLiDAR()

        if heading <= -135:
            #Collect Data from Walls 2 and 1
            pwm.value = self.adjustAngle(180+heading+90)/100
            time.sleep(.5)
            x = self.readLiDAR()
            pwm.value = self.adjustAngle(90+heading+90)/100
            time.sleep(.5)
            y = self.readLiDAR()

        if heading > 0 and heading <= 45:
            #Collect Data from Walls 4 and 3
            pwm.value = self.adjustAngle(90+heading)/100
            time.sleep(.5)
            x = maxX- self.readLiDAR()
            pwm.value = self.adjustAngle(0+heading)/100
            time.sleep(.5)
            y = maxY- self.readLiDAR()

        if heading > 45 and heading <= 90:
            #Collect Data from Walls 4 and 3
            pwm.value = self.adjustAngle(90+heading)/100
            time.sleep(.5)
            x = maxX- self.readLiDAR()
            pwm.value = self.adjustAngle(0+heading)/100
            time.sleep(.5)
            y = maxY- self.readLiDAR()

        if heading > 90 and heading <= 135:
            #Collect Data from Walls 2 and 3
            pwm.value = self.adjustAngle(heading-90)/100
            time.sleep(.5)
            x = self.readLiDAR()
            pwm.value = self.adjustAngle(heading)/100
            time.sleep(.5)
            y = maxY-self.readLiDAR()

        if heading > 135:
            #Collect Data from Walls 2 and 3
            pwm.value = self.adjustAngle(heading-90)/100
            time.sleep(.5)
            x = self.readLiDAR()
            pwm.value = self.adjustAngle(heading)/100
            time.sleep(.5)
            y = maxY- self.readLiDAR()

        coordinates.append(x)
        coordinates.append(y)
        return coordinates



class MotorR(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor
    connected to a bi-directional motor driver circuit (i.e. an `H-bridge`_).

    """
    def __init__(self, pwmR = 18, forwardR=24, backwardR=23,pin_factory=None):

        super(MotorR, self).__init__(
                pwmR=PWMOutputDevice(pwmR, pin_factory=pin_factory),
                fwdR=DigitalOutputDevice(forwardR, pin_factory=pin_factory),
                revR=DigitalOutputDevice(backwardR, pin_factory=pin_factory),
                _order=('pwmR','fwdR','revR'),
                pin_factory=pin_factory
        )

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward), with 0 representing
        stopped.
        """
        if (self.fwdR.value == 1) & (self.revR.value == 0):
            return self.pwmR
        elif (self.fwdR.value ==0) & (self.revR.value ==1):
            return - self.pwmR
        else:
            return 0

    @value.setter
    def value(self, value):
        if not -1 <= value <= 1:
            raise OutputDeviceBadValue("Motor value must be between -1 and 1")
        if value > 0:
            try:
                self.forward(value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        elif value < 0:
            try:
               self.backward(-value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        else:
            self.stop()

    @property
    def is_active(self):
        """
        Returns ``True`` if the motor is currently running and ``False``
        otherwise.
        """
        return self.value != 0

    def forward(self, speed=0.5):
        """
        Drive the motor forwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if ``pwm`` was
            ``True`` when the class was constructed (and only 0 or 1 if not).
        """
        if not 0 <= speed <= 1:
            raise ValueError('forward speed must be between 0 and 1')
        self.revR.off()
        self.fwdR.on()
        self.pwmR.value = speed


    def backward(self, speed=0.5):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if ``pwm`` was
            ``True`` when the class was constructed (and only 0 or 1 if not).
        """
        self.revR.on()
        self.fwdR.off()
        self.pwmR.value = speed


    def stop(self):
        """
        Stop the motor.
        """
        self.revR.off()
        self.fwdR.off()
        self.pwmR.off()

class MotorL(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor
    connected to a bi-directional motor driver circuit (i.e. an `H-bridge`_).

    """
    def __init__(self, pwmL = 19, forwardL=22, backwardL=27,pin_factory=None):

        super(MotorL, self).__init__(
                pwmL=PWMOutputDevice(pwmL, pin_factory=pin_factory),
                fwdL=DigitalOutputDevice(forwardL, pin_factory=pin_factory),
                revL=DigitalOutputDevice(backwardL, pin_factory=pin_factory),
                _order=('pwmL','fwdL','revL'),
                pin_factory=pin_factory
        )

    @property
    def value(self):
        """
        Represents the speed of the motor as a floating point value between -1
        (full speed backward) and 1 (full speed forward), with 0 representing
        stopped.
        """
        if (self.fwdL.value == 1) & (self.revL.value == 0):
            return self.pwmL
        elif (self.fwdL.value ==0) & (self.revL.value ==1):
            return - self.pwmL
        else:
            return 0

    @value.setter
    def value(self, value):
        if not -1 <= value <= 1:
            raise OutputDeviceBadValue("Motor value must be between -1 and 1")
        if value > 0:
            try:
                self.forward(value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        elif value < 0:
            try:
               self.backward(-value)
            except ValueError as e:
                raise OutputDeviceBadValue(e)
        else:
            self.stop()

    @property
    def is_active(self):
        """
        Returns ``True`` if the motor is currently running and ``False``
        otherwise.
        """
        return self.value != 0

    def forward(self, speed=0.5):
        """
        Drive the motor forwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if ``pwm`` was
            ``True`` when the class was constructed (and only 0 or 1 if not).
        """
        if not 0 <= speed <= 1:
            raise ValueError('forward speed must be between 0 and 1')
        self.revL.off()
        self.fwdL.on()
        self.pwmL.value = speed


    def backward(self, speed=0.5):
        """
        Drive the motor backwards.

        :param float speed:
            The speed at which the motor should turn. Can be any value between
            0 (stopped) and the default 1 (maximum speed) if ``pwm`` was
            ``True`` when the class was constructed (and only 0 or 1 if not).
        """
        self.revL.on()
        self.fwdL.off()
        self.pwmL.value = speed


    def stop(self):
        """
        Stop the motor.
        """
        self.revL.off()
        self.fwdL.off()
        self.pwmL.off()


def main(args):

    time.sleep(30)

    global sockConn
    global sonarObj
    global imuObj
    global initialHeading
    global pwm
    sockConn = SocketConnect(12000) ## starts recv and send threads; recv thread passes cmds directly to executeCommand to control motor
    sonarObj = Sonar()
    imuObj = ImuPosHeading()
    initialHeading = imuObj.readIMU(0)
    pwm= PWMOutputDevice(25)
    pwm.frequency = 50

    



    '''
            while sockConn.connected:
                heading = imuObj.readIMU(initialHeading)

                obstLocString = sonarObj.getObstacleLoc(heading)
                if len(obstLocString) is not 0:
                    sockConn.addToSendMessage(obstLocString, 1) # 1 for obst loc, 0 for marvin loc

            #sonarObj.stopReading()

        sonarObj.disableSonar('front')
        sonarObj.disableSonar('back')
        sonarObj.disableSonar('left')
        sonarObj.disableSonar('right')

    '''





if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
