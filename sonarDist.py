#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import time,sleep
##try:
##    from statistics import median
##except ImportError:
##    from .compat import median

class DistanceSensor():

    def __init__( self):
        GPIO.setmode(GPIO.BCM)
        self.trigger0 = 4 
        self.echo0 = 17
        self.trigger1 = 6 
        self.echo1 = 5
        self.trigger2 = 12
        self.echo2 = 16
        self.trigger3 = 26
        self.echo3 = 13
        self.speed_of_sound = 34326 # m/s
        GPIO.setup(self.trigger0,GPIO.OUT)
        GPIO.setup(self.echo0, GPIO.IN)
        GPIO.setup(self.trigger1,GPIO.OUT)
        GPIO.setup(self.echo1, GPIO.IN)
        GPIO.setup(self.trigger2,GPIO.OUT)
        GPIO.setup(self.echo2, GPIO.IN)
        GPIO.setup(self.trigger3,GPIO.OUT)
        GPIO.setup(self.echo3, GPIO.IN)

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
        dist = []
        GPIO.output(self.trigger0, True)
        sleep(0.00001)
        GPIO.output(self.trigger0, False)
        

        StartTime = time()
        StopTime = time()
        
        while(GPIO.input(self.echo0) == 0):
            StartTime = time()
        while(GPIO.input(self.echo0) == 1):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance0 = (TimeElapsed *34326) / 2

        dist.append(distance0)

        GPIO.output(self.trigger1, True)
        sleep(0.00001)
        GPIO.output(self.trigger1, False)
        

        StartTime = time()
        StopTime = time()
        
        while(GPIO.input(self.echo1) == 0):
            StartTime = time()
        while(GPIO.input(self.echo1) == 1):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance1 = (TimeElapsed *34326) / 2

        dist.append(distance1)

        GPIO.output(self.trigger2, True)
        sleep(0.00001)
        GPIO.output(self.trigger2, False)
        

        StartTime = time()
        StopTime = time()
        
        while(GPIO.input(self.echo2) == 0):
            StartTime = time()
        while(GPIO.input(self.echo2) == 1):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance2 = (TimeElapsed *34326) / 2

        dist.append(distance2)

        GPIO.output(self.trigger3, True)
        sleep(0.00001)
        GPIO.output(self.trigger3, False)
        

        StartTime = time()
        StopTime = time()
        
        while(GPIO.input(self.echo3) == 0):
            StartTime = time()
        while(GPIO.input(self.echo3) == 1):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance3 = (TimeElapsed *34326) / 2

        dist.append(distance3)
       
       

        
        
        return dist
'''
 def getObstacleLoc(self, heading):
        
        Gives obstacle locations as x,y displacements from vechicle
        ex: if the heading is 0 degree and th front sensor reads an object that is 20cm away and the left sensor reads an object that is 30 cm away, then '[20,0] [0,30]' is
        returned
    
        xyListString = ''
        if len(self.distData) != 0:
            for i in  range(0,len(self.distData)):
                if self.distData[i][0] == 0: # if front sensor
                    d = self.distData[i][1]
                    if (0 <= heading ) and (heading <= 90):
                        theta = heading
                        x = d * cos(theta)
                        y = d * sin(theta)
                    elif (90 < heading) and (heading < 180):
                        theta = 180 - heading
                        x = -1 * d * cos(theta)
                        y = d * sin(theta)

                    elif (-180 < heading) and (heading < -90):
                        theta = heading + 180
                        x = -1 * d * cos(theta)
                        y = -1 * d * sin(theta)

                    elif (-90 < heading ) and (heading < 0):
                        theta = abs(heading)
                        x = d * cos(theta)
                        y = -1 * d * sin(theta)

                elif self.distData[i][0] == 1: # if back sensor, ~ 6' from lidar
                    d = self.distData[i][1] + (6 * 2.54)
                    if (0 <= heading) and (heading <= 90):
                        theta = heading
                        x = - 1 * d * cos(theta)
                        y = - 1 * d * sin(theta)
                    elif (90 < heading) and (heading < 180):
                        theta = 180 - heading
                        x = d * cos(theta)
                        y = - 1 * d * sin(theta)

                    elif (-180 < heading) and (heading < -90):
                        theta = heading + 180
                        x = d * cos(theta)
                        y = d * sin(theta)

                    elif (-90 < heading) and (heading < 0):
                        theta = abs(heading)
                        x = -1 * d * cos(theta)
                        y = d * sin(theta)

                elif self.distData[i][0] == 2: # if left sensor, ~
                    d = self.distData[i][1]
                    if (0 <= heading ) and (heading <= 90):
                        theta = 90 - heading
                        dx = - 6 * cos(theta)
                        dy = - 6 * sin(theta)
                        x = -1 * d * cos(theta)
                        y = d * sin(theta)

                    elif (90 < heading) and (heading < 180):
                        theta = 90 - (180 - heading)
                        dx = cos(theta) * 6
                        dy = - sin(theta) * 6
                        x = - 1 * d * cos(theta)
                        y = - 1 * d * sin(theta)

                    elif (-180 < heading) and (heading < -90):
                        theta = 90 - (heading + 180)
                        dx = cos(theta) * 6
                        dy = sin(theta) * 6
                        x =  d * cos(theta)
                        y = -1 * d * sin(theta)

                    elif (-90 < heading ) and (heading < 0):
                        theta = 90 - abs(heading)
                        dx = - cos(theta) * 6
                        dy = sin(theta) * 6
                        x = d * cos(theta)
                        y = d * sin(theta)

                    x = x + dx
                    y = y + dy

                elif self.distData[i][0] == 3: # if right sensor
                    d = self.distData[i][1]
                    if (0 <= heading ) and (heading <= 90):
                        theta = 90 - heading
                        dx = - cos(theta) * 6
                        dy = - sin(theta) * 6
                        x = d * cos(theta)
                        y = -1 * d * sin(theta)

                    elif (90 < heading) and (heading < 180):
                        theta = 90 - (180 - heading)
                        dx = cos(theta) * 6
                        dy = - sin(theta) * 6
                        x = d * cos(theta)
                        y = d * sin(theta)

                    elif (-180 < heading) and (heading < -90):
                        theta = 90 - (heading + 180)
                        dx = cos(theta) * 6
                        dy = sin(theta) * 6
                        x = -1 * d * cos(theta)
                        y =  d * sin(theta)

                    elif (-90 < heading ) and (heading < 0):
                        theta = 90 - abs(heading)
                        dx = - cos(theta) * 6
                        dy = sin(theta) * 6
                        x = -1 * d * cos(theta)
                        y =  -1 * d * sin(theta)

                xyString = '[' + str(x) + ',' + str(y) + ']'
                if i is not len(self.distData):
                    xyString = xyString + ' '
                xyListString = xyListString + xyString
        self.distData = []

        return xyListString
'''

##sonarObj = DistanceSensor()
##
##while(1):
##    sleep(0.5)
##    sonardist = sonarObj.distance
##
##    print('sonar distance: ' + str(sonardist[0]) + str(sonardist[1]) + str(sonardist[2]) + str(sonardist[3]))
##
##
