import RPi.GPIO as GPIO
import time
import traceback

GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER_First = 4
GPIO_ECHO_First = 17

## GPIO Occupied 18 27 22 19 23 24
"""

GPIO_TRIGGER_Second = 6
GPIO_ECHO_Second = 5


## Green : Echo, Purple : Trigger
GPIO_TRIGGER_Third = 12
GPIO_ECHO_Third = 16


##
GPIO_TRIGGER_Fourth = 26 
GPIO_ECHO_Fourth = 13
"""

GPIO.setup(GPIO_TRIGGER_First, GPIO.OUT)
GPIO.setup(GPIO_ECHO_First, GPIO.IN)

"""
GPIO.setup(GPIO_TRIGGER_Second, GPIO.OUT)
GPIO.setup(GPIO_ECHO_Second, GPIO.IN)

GPIO.setup(GPIO_TRIGGER_Third, GPIO.OUT)
GPIO.setup(GPIO_ECHO_Third, GPIO.IN)
##
GPIO.setup(GPIO_TRIGGER_Fourth, GPIO.OUT)
GPIO.setup(GPIO_ECHO_Fourth, GPIO.IN)
"""
GPIO.setwarnings(False)

def distance(sonarID):
    if sonarID == 1:
        Trigger =GPIO_TRIGGER_First
        Echo = GPIO_ECHO_First
    elif sonarID == 2:
        Trigger =GPIO_TRIGGER_Second
        Echo = GPIO_ECHO_Second
    elif sonarID == 3:
        print("code came here")
        try:
            Trigger =GPIO_TRIGGER_Third
            Echo = GPIO_ECHO_Third
        except:
            traceback.print_exc()
    elif sonarID == 4:
        Trigger = GPIO_TRIGGER_Fourth
        Echo = GPIO_ECHO_Fourth

    GPIO.output(Trigger, True)
    time.sleep(0.00001)
    GPIO.output(Trigger, False)
    StartTime = time.time()
    StopTime = time.time()

    while GPIO.input(Echo) == 0:
        StartTime = time.time()
##        print("starting time");
    while GPIO.input(Echo) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed *34300) / 2
    return distance


if __name__ == '__main__':
##        try:
            while True:
##                dist = distance(1)
##                print("the first distance = %.2f cm" %dist)
##                time.sleep(1)
                dist2 = distance(1)
                print("the second distance = %.2f cm" %dist2)
                time.sleep(0.3)
"""
                try:
                    dist3 = distance(3)
                    print("the third distance = %.2f cm" %dist3)
                    time.sleep(1)
                    dist4 = distance(4)
                    print("the fourth distance = %.2f cm" %dist4)
                    time.sleep(1)
                except:
                    traceback.print_exc()
                    

        except KeyboardInterrupt:
            print("Measurment Stopped")
            GPIO.cleanup()
"""
