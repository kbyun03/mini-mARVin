import RPi.GPIO as GPIO                                                                                                                                                                                                                                                                                                          
import time

def forwardRight(speed = 25):
    GPIO.output(23,1)
    GPIO.output(24,0)
    my_pwm1.start(speed)

def reverseRight (speed = 25):
    GPIO.output(23,0)
    GPIO.output(24,1)
    my_pwm1.start(speed)
    
def forwardLeft(speed=25):
    GPIO.output(22, 1)
    GPIO.output(27,0)
    my_pwm2.start(speed)

def reverseLeft(speed=25):
    GPIO.output(22,0)
    GPIO.output(27,1)
    my_pwm2.start(speed)

def goForward(speed = 25):
    forwardLeft(speed)
    forwardRight(speed)

def goBackward(speed = 25):
    reverseLeft(speed)
    reverseRight(speed)

def turnRight(speed = 25):
    forwardRight(speed)
    reverseLeft(speed)

def turnLeft(speed = 25):
    forwardLeft(speed)
    reverseRight(speed)

def stopLeft():
    my_pwm2.stop()
    
def stopRight():
    my_pwm1.stop()
    
def stop():
    stopLeft()
    stopRight()

def main(args):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.OUT) # pwm Right
    GPIO.setup(23, GPIO.OUT) # forward Right
    GPIO.setup(24, GPIO.OUT) # reverse Right

    GPIO.setup(19, GPIO.OUT) # pwm Left
    GPIO.setup(22, GPIO.OUT) # forward Right
    GPIO.setup(27, GPIO.OUT) # reverse Right


    global my_pwm1
    my_pwm1 = GPIO.PWM(18,100)
    global my_pwm2
    my_pwm2 = GPIO.PWM(19,100)
    goForward()
    

    command = input("Enter a motor command: ")
##        prev_command = None
##        if command == 1:
####            if prev_command != "FORWARD":
##                stop()
##                prev_command = "FORWARD"
##                goForward()
##        if command == 2:
##            if prev_command != "REVERSE":
##                stop()
##                prev_command = "REVERSE"
##                goBackward()
##        if command == 3:
##            if prev_command != "RIGHT":
##                stop()
##                prev_command = "RIGHT"
##                turnRight()
##        if command == 4:
##            if prev_command != "LEFT":
##                stop()
##                prev_command = "LEFT"
##                turnLeft()
##        if command ==  5:
##            if prev_command != "STOP":
##                stop()
##                prev_command = "STOP"
##        if command == 6:
##            stop()
##            GPIO.cleanup()
##            return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
