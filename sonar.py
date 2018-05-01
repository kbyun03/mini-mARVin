#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import time,sleep
##try:
##    from statistics import median
##except ImportError:
##    from .compat import median

class DistanceSensor():

    def __init__( self, echo=None, trigger=None):
        GPIO.setmode(GPIO.BCM)
        self.trigger = trigger
        self.echo = echo
        self.speed_of_sound = 34326 # m/s
        GPIO.setup(self.trigger,GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)

    @property
    def distance(self):
        """
        Returns the current distance measured by the sensor in meters. Note
        that this property will have a value between 0 and
        :attr:`max_distance`.
        """
        return self._read()

    def close(self):
        GPIO.cleanup()
    
    def _read(self):
        # Make sure the echo pin is low then ensure the echo event is clear
        GPIO.output(self.trigger, True)
        sleep(0.00001)
        GPIO.output(self.trigger, False)
        

        StartTime = time()
        StopTime = time()
        
        while(GPIO.input(self.echo) == 0):
            StartTime = time()
        while(GPIO.input(self.echo) == 1):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed *34326) / 2
       

        
        
        return distance


##sonarObj = DistanceSensor(17,4)
##
##while(1):
##    sleep(0.5)
##    mydist = []
##    for i in range(0,12):
##        sonardist = sonarObj.distance
##        mydist.append(sonardist)
##        print('sonar distance: ' + str(sonardist))
##    mydist.sort()
##    print('median dist: ' + str(mydist[5]))
