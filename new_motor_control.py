from gpiozero.output_devices import PWMOutputDevice, DigitalOutputDevice
from gpiozero.devices import GPIODevice, Device, CompositeDevice
from gpiozero.threads import GPIOThread
from gpiozero.mixins import SourceMixin
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
        self.socket.listen(10)
        debug('listening...')
        self.tConn = Thread(name = 'conn', target = self.checkConnection)
        #tSend = threading.Thread(name = 'send', target = self.socketSender)
        self.tRecv = Thread(name = 'recv', target = self.socketReciever)
        self.mutex = Lock()
        self.tConn.start()
        

    def checkConnection(self):
        while (1):
            self.mutex.acquire()
            if (not self.connected) and (not self.openConnection):
                self.conn, self.addr = self.socket.accept()
                debug('connected')
                self.connected = True
                self.openConnection = True
                self.mutex.release()
                #tSend.start()
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
            

class MotorR(SourceMixin, CompositeDevice):
    """
    Extends :class:`CompositeDevice` and represents a generic motor
    connected to a bi-directional motor driver circuit (i.e. an `H-bridge`_).

    Attach an `H-bridge`_ motor controller to your Pi; connect a power source
    (e.g. a battery pack or the 5V pin) to the controller; connect the outputs
    of the controller board to the two terminals of the motor; connect the
    inputs of the controller board to two GPIO pins.

    .. _H-bridge: https://en.wikipedia.org/wiki/H_bridge

    The following code will make the motor turn "forwards"::

        from gpiozero import Motor

        motor = Motor(17, 18)
        motor.forward()

    :param int forward:
        The GPIO pin that the forward input of the motor driver chip is
        connected to.

    :param int backward:
        The GPIO pin that the backward input of the motor driver chip is
        connected to.

    :param bool pwm:
        If ``True`` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If ``False``, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
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

    Attach an `H-bridge`_ motor controller to your Pi; connect a power source
    (e.g. a battery pack or the 5V pin) to the controller; connect the outputs
    of the controller board to the two terminals of the motor; connect the
    inputs of the controller board to two GPIO pins.

    .. _H-bridge: https://en.wikipedia.org/wiki/H_bridge

    The following code will make the motor turn "forwards"::

        from gpiozero import Motor

        motor = Motor(17, 18)
        motor.forward()

    :param int forward:
        The GPIO pin that the forward input of the motor driver chip is
        connected to.

    :param int backward:
        The GPIO pin that the backward input of the motor driver chip is
        connected to.

    :param bool pwm:
        If ``True`` (the default), construct :class:`PWMOutputDevice`
        instances for the motor controller pins, allowing both direction and
        variable speed control. If ``False``, construct
        :class:`DigitalOutputDevice` instances, allowing only direction
        control.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).
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

sockConn = SocketConnect(12000)
