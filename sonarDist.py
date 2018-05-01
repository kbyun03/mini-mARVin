#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from time import time,sleep
from math import cos, sin
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
        distTest = []
        i = 0
        while i < 30:
            GPIO.output(self.trigger0, True)
            sleep(0.00001)
            GPIO.output(self.trigger0, False)


            StartTime = time()
            StopTime = time()
            
            tStart = time()
            while(GPIO.input(self.echo0) == 0):
                tNow = time()
                StartTime = time()
                if (tNow - tStart) >= 5:
                    GPIO.output(self.trigger0, True)
                    sleep(0.00001)
                    GPIO.output(self.trigger0, False)
                    tStart = time()
                    continue
                    
            while(GPIO.input(self.echo0) == 1):
                StopTime = time()
            TimeElapsed = StopTime - StartTime
            distance0 = (TimeElapsed *34326) / 2
            if distance0 < 200:
                i = i + 1
                print('Front: ' + str(distance0))
                distTest.append(distance0)

        distTest.sort()
        length = round(len(distTest)/2)
        minDist = distTest[0]

        correctedDist = []
        for i in distTest:

            if minDist < 2:
                minDist = i

            if (i > 2) or (i == 2) :
                if (i - minDist) <= 5:
                    correctedDist.append(i)
        print('corrected list: ' + str(correctedDist))

        if(len(correctedDist) != 0):
            distance0 = sum(correctedDist) / float(len(correctedDist))

        else:
            distance0 = 0
##        distance0 = distTest[length]
##        print('median dist: ' + str(distance0))


        dist.append(distance0)

##        distTest = []
##        i = 0
##        while i < 30:
##            GPIO.output(self.trigger1, True)
##            sleep(0.00001)
##            GPIO.output(self.trigger1, False)
##
##
##
##
##            StartTime = time()
##            StopTime = time()
##            
##            tStart = time()
##            while(GPIO.input(self.echo1) == 0):
##                tNow = time()
##                StartTime = time()
##                if (tNow - tStart) >= 5:
##                    GPIO.output(self.trigger1, True)
##                    sleep(0.00001)
##                    GPIO.output(self.trigger1, False)
##                    tStart = time()
##                    continue
##                    
##            while(GPIO.input(self.echo1) == 1):
##                StopTime = time()
##            TimeElapsed = StopTime - StartTime
##            distance1 = (TimeElapsed *34326) / 2
##            if distance1 < 1000:
##                i = i + 1
##                print('Back: ' + str(distance1))
##                distTest.append(distance1)
##
##        distTest.sort()
##        minDist = distTest[0]
##
##        correctedDist = []
##        for i in distTest:
##
##            if minDist < 2:
##                minDist = i
##
##            if (i > 2) or (i == 2) :
##                if (i - minDist) <= 5:
##                    correctedDist.append(i)
##        print('corrected list: ' + str(correctedDist))
##
##        distance1 = sum(correctedDist) / float(len(correctedDist))
##
##
##        dist.append(distance1)
##
##        distTest = []
##        i = 0
##        while i < 30:
##            GPIO.output(self.trigger2, True)
##            sleep(0.00001)
##            GPIO.output(self.trigger2, False)
##
##
##
##
##            StartTime = time()
##            StopTime = time()
##            
##            tStart = time()
##            while(GPIO.input(self.echo2) == 0):
##                tNow = time()
##                StartTime = time()
##                if (tNow - tStart) >= 5:
##                    GPIO.output(self.trigger2, True)
##                    sleep(0.00001)
##                    GPIO.output(self.trigger2, False)
##                    tStart = time()
##                    continue
##                    
##            while(GPIO.input(self.echo2) == 1):
##                StopTime = time()
##            TimeElapsed = StopTime - StartTime
##            distance2 = (TimeElapsed *34326) / 2
##            if distance2 < 1000:
##                i = i + 1
##                print('Left: ' + str(distance2))
##                distTest.append(distance2)
##
##        distTest.sort()
##        minDist = distTest[0]
##
##        correctedDist = []
##        for i in distTest:
##
##            if minDist < 2:
##                minDist = i
##
##            if (i > 2) or (i == 2) :
##                if (i - minDist) <= 5:
##                    correctedDist.append(i)
##        print('corrected list: ' + str(correctedDist))
##
##        distance2 = sum(correctedDist) / float(len(correctedDist))
##
##
##        dist.append(distance2)
##
##        distTest = []
##        i = 0
##        while i < 30:
##            GPIO.output(self.trigger3, True)
##            sleep(0.00001)
##            GPIO.output(self.trigger3, False)
##
##
##
##
##            StartTime = time()
##            StopTime = time()
##            
##            tStart = time()
##            while(GPIO.input(self.echo3) == 0):
##                tNow = time()
##                StartTime = time()
##                if (tNow - tStart) >= 5:
##                    GPIO.output(self.trigger3, True)
##                    sleep(0.00001)
##                    GPIO.output(self.trigger3, False)
##                    tStart = time()
##                    continue
##                    
##            while(GPIO.input(self.echo3) == 1):
##                StopTime = time()
##            TimeElapsed = StopTime - StartTime
##            distance3 = (TimeElapsed *34326) / 2
##            if distance3 < 1000:
##                i = i + 1
##                print('Right: ' + str(distance3))
##                distTest.append(distance3)
##
##        distTest.sort()
##        minDist = distTest[0]
##
##        correctedDist = []
##        for i in distTest:
##
##            if minDist < 2:
##                minDist = i
##
##            if (i > 2) or (i == 2) :
##                if (i - minDist) <= 5:
##                    correctedDist.append(i)
##        print('corrected list: ' + str(correctedDist))
##
##        distance3 = sum(correctedDist) / float(len(correctedDist))
##
##
##        dist.append(distance3)
##              

        return dist

    def getObstacleLoc(self, heading):
        self.distData = self.distance

    
        xyListString = ''

        d = self.distData[0]
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


        xyString = '[' + str(x) + ',' + str(y) + ']'

        return xyString


##sonarObj = DistanceSensor()
##
##while(1):
##    sleep(0.5)
##    sonardist = sonarObj.distance
##
##    print('sonar distance: ' + str(sonardist[0]) + str(sonardist[1]) + str(sonardist[2]) + str(sonardist[3]))
##
##
