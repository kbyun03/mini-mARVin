from gpiozero.output_devices import PWMOutputDevice, DigitalOutputDevice
from gpiozero.devices import GPIODevice, Device, CompositeDevice
from gpiozero.threads import GPIOThread
from gpiozero.mixins import SourceMixin
from gpiozero.input_devices import DistanceSensor
from threading import Lock, Thread
import socket
import time
import sys

VERBOSE = True

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
        self.messageType = {0:'MARV', 1:'OBST'}
        debug('listening...')
        self.tConn = Thread(name = 'conn', target = self.checkConnection)
        self.tSend = threading.Thread(name = 'send', target = self.socketSender)
        self.tRecv = Thread(name = 'recv', target = self.socketReciever)
        self.mutex = Lock()
        self.tConn.start()

    def addToSendMessage(self, msg, type):
        '''
            msg is data as a string of x,y coord
            type is either 0 for marvin loc or 1 for obstacle loc

            message types will be delineated by ';', data values (such as diff obstacle locations)
            will be delineated by ' '

         '''
        self.mutex.acquire()
        self.sendMessage = self.sendMessage + self.messageType[type]
        for i in len(self.messageType):
            self.sendMessage = self.sendMessage + self.messageType[i] + msg + ';'
        self.mutex.release()

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
            if self.quit:
                if self.openConnection or self.connected:
                    self.closeConn()
                    self.openConnection = False
                break


   def socketSender(self):
       while(1):
           if len(self.sendMessage) is not 0:
               try:
                   self.mutex.acquire()
                   self.conn.sendall(self.sendMessage.encode())
                   debug('sending message: ' + self.sendMessage)
                   self.sendMessage = ''
                   self.mutex.release()
               except socket.error as eMsg:
                   debug('exception occured in conn.sendall():' + str(eMsg))
                   self.mutex.acquire()
                   self.connected = False
                   self.mutex.release()
                   break

    def socketReciever(self):
        while (1):
            cmd = ''
            try:
                cmd = self.conn.recv(4096)
                cmdStr = str(cmd.decode())
                debug('recieved command: ' + cmdStr)
            except socket.error as msg:
                debug('exception in conn.recv():' + str(msg))
                self.mutex.acquire()
                self.connected = False
                self.mutex.release()
                break

            if len(cmdStr) == 0:
                self.mutex.acquire()
                self.connected = False
                self.mutex.release()
                break

            self.executeCommand(cmdStr)

    def closeConn(self):
        try:
            #self.tSend.join()
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

class Sonar():
    def __init__(self):
        self.sonarSensors = { 'front': 0, 'back': 1, 'left': 2, 'right':3}

        self.sonar0 = DistanceSensor(echo=17, trigger=14, max_distance = 4) # front
        self.sonar1 = DistanceSensor(echo=13, trigger=26,max_distance = 4 ) # back
        self.sonar2 = DistanceSensor(echo=5, trigger = 6, max_distance = 4) # left
        self.sonar3 = DistanceSensor(echo=16, trigger=12, max_distance = 4) # right

        self.distData = [] # list of data read from sonars... each entry is in form [sonarNum, dist]

        self.currSonars = [] # this list will represent the currently enabled sonar sensors at any time
        self.currSonarInd = []

        self.obstacleLoc = [] # this list will hold obstacle locations as X,Y coordinates

        self.killThread = False # this will be set
        self.tRead = Thread(target = readSonar, name = 'read')

    def enableSonar(self, sonarName):
        '''sonarName should be given as a string: 'front' '''

        self.currSonars.append(getattr(self, 'sonar' + str(self.sonarSensors[sonarToEnable])))
        self.currSonarInd.append(sonarName)

    def disableSonar(self, sonarName):
        '''sonarName should be given as a string: 'front' '''
        ind = self.currSonarInd.index(sonarName)
        self.currSonars[ind].close()
        self.currSonarInd.pop(ind)
        self.currSonars.pop(ind)

    def startReading(self):
        ''' kicks off thread'''
        tRead.start()

    def stopReading(self):
        self.killThread = True;

    def readSonar(self): # this is a thread
        ''' adds distance read to distance list; dist is in m '''
        while(1):
            for i in self.currSonarInd:
                self.distData.append([self.sonarSensors[i], self.currSonars[i].distance()])

            if self.killThread:
                break

    def getObstacleLoc():
        '''
        Gives obstacle locations as x,y displacements from vechicle
        ex: if the front sensor reads an object that is 20cm away and the
            left sensor reads an object that is 30 cm away, then '[20,0] [0,30]' is
            returned
        '''
        xyListString = ''
        if len(self.distData) != 0:
            for i in len(self.distData):
                if self.distData[i][1] == 0: # if front sensor
                    xyString = '[' + str(self.distData[i][2]) + ',0]'
                    if i is not len(self.distData):
                        xyString = xyString + ' '

                elif self.distData[i][1] == 1: # if back sensor
                    xyString = '[' + str(-1*self.distData[i][2]) + ',0]'
                    if i is not len(self.distData):
                        xyString = xyString + ' '

                elif self.distData[i][1] == 2: # if left sensor
                    xyString = '[0,' + str(self.distData[i][2]) + ']'
                    if i is not len(self.distData):
                        xyString = xyString + ' '

                elif self.distData[i][1] == 3: # if right sensor
                    xyString = '[0,' + str(-1*self.distData[i][2]) + ']'
                    if i is not len(self.distData):
                        xyString = xyString + ' '

                self.distData.pop(i)
                xyListString = xyListString + xyString

        return xyList



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

    sockConn = SocketConnect(12000) ## starts recv and send threads; recv thread passes cmds directly to executeCommand to control motor
     self.sonarObj = Sonar()
    while(1):
        obstLocString = ''
        self.sonarObj.enableSonar('front')
        self.sonarObj.enableSonar('back')
        self.sonarObj.enableSonar('left')
        self.sonarObj.enableSonar('right')
        self.sonarObj.startReading()
        while sockConn.connected:
            obstLocString = self.sonarObj.getObstacleLoc()
            if len(obstLocString) is not 0:
                self.sockConn.addToSendMessage(obstLocString, 1) # 1 for obst loc, 0 for marvin loc

        self.sonarObj.stopReading()
        self.sonarObj.disableSonar('front')
        self.sonarObj.disableSonar('back')
        self.sonarObj.disableSonar('left')
        self.sonarObj.disableSonar('right')





if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
