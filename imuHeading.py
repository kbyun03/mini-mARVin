import serial
import time
import sys
import math
from IMU import *
import datetime
import os
from threading import Thread



class ImuPosHeading():
    def __init__(self):
        self.RAD_TO_DEG = 57.29578
        self.M_PI = 3.14159265358979323846
        self.G_GAIN = 0.070     # [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
        self.AA =  0.40         # Complementary filter constant
        self.MAG_LPF_FACTOR = 0.4   # Low pass filter constant magnetometer
        self.ACC_LPF_FACTOR = 0.4   # Low pass filter constant for accelerometer
        self.ACC_MEDIANTABLESIZE = 9        # Median filter table size for accelerometer. Higher = smoother but a longer delay
        self.MAG_MEDIANTABLESIZE = 9        # Median filter table size for magnetometer. Higher = smoother but a longer delay

        #Kalman filter variables
        self.Q_angle = 0.02
        self.Q_gyro = 0.0015
        self.R_angle = 0.005
        self.y_bias = 0.0
        self.x_bias = 0.0
        self.XP_00 = 0.0
        self.XP_01 = 0.0
        self.XP_10 = 0.0
        self.XP_11 = 0.0
        self.YP_00 = 0.0
        self.YP_01 = 0.0
        self.YP_10 = 0.0
        self.YP_11 = 0.0
        self.KFangleX = 0.0
        self.KFangleY = 0.0

    def kalmanFilterY(self,accAngle, gyroRate, DT):
        y=0.0
        S=0.0

        self.KFangleY = self.KFangleY + DT * (gyroRate - self.y_bias)

        self.YP_00 = self.YP_00 + ( - DT * (self.YP_10 + self.YP_01) + self.Q_angle * DT )
        self.YP_01 = self.YP_01 + ( - DT * self.YP_11 )
        self.YP_10 = self.YP_10 + ( - DT * self.YP_11 )
        self.YP_11 = self.YP_11 + ( + self.Q_gyro * DT )

        y = accAngle - self.KFangleY
        S = self.YP_00 + self.R_angle
        K_0 = self.YP_00 / S
        K_1 = self.YP_10 / S

        self.KFangleY = self.KFangleY + ( K_0 * y )
        self.y_bias = self.y_bias + ( K_1 * y )

        self.YP_00 = self.YP_00 - ( K_0 * self.YP_00 )
        self.YP_01 = self.YP_01 - ( K_0 * self.YP_01 )
        self.YP_10 = self.YP_10 - ( K_1 * self.YP_00 )
        self.YP_11 = self.YP_11 - ( K_1 * self.YP_01 )

        return self.KFangleY

    def kalmanFilterX(self,accAngle, gyroRate, DT):
        x=0.0
        S=0.0

        self.KFangleX = self.KFangleX + DT * (gyroRate - self.x_bias)

        self.XP_00 = self.XP_00 + ( - DT * (self.XP_10 + self.XP_01) + self.Q_angle * DT )
        self.XP_01 = self.XP_01 + ( - DT * self.XP_11 )
        self.XP_10 = self.XP_10 + ( - DT * self.XP_11 )
        self.XP_11 = self.XP_11 + ( + self.Q_gyro * DT )

        x = accAngle - self.KFangleX
        S = self.XP_00 + self.R_angle
        K_0 = self.XP_00 / S
        K_1 = self.XP_10 / S

        self.KFangleX = self.KFangleX + ( K_0 * x )
        self.x_bias = self.x_bias + ( K_1 * x )

        self.XP_00 = self.XP_00 - ( K_0 * self.XP_00 )
        self.XP_01 = self.XP_01 - ( K_0 * self.XP_01 )
        self.XP_10 = self.XP_10 - ( K_1 * self.XP_00 )
        self.XP_11 = self.XP_11 - ( K_1 * self.XP_01 )

        return self.KFangleX

    def readIMU(self,initialHeading):
        a = datetime.datetime.now()
        gyroXangle = 0.0
        gyroYangle = 0.0
        gyroZangle = 0.0
        CFangleX = 0.0
        CFangleY = 0.0
        CFangleXFiltered = 0.0
        CFangleYFiltered = 0.0
        kalmanX = 0.0
        kalmanY = 0.0
        oldXMagRawValue = 0
        oldYMagRawValue = 0
        oldZMagRawValue = 0
        oldXAccRawValue = 0
        oldYAccRawValue = 0
        oldZAccRawValue = 0

        #Setup the tables for the mdeian filter. Fill them all with '1' soe we dont get devide by zero error
        acc_medianTable1X = [1] * self.ACC_MEDIANTABLESIZE
        acc_medianTable1Y = [1] * self.ACC_MEDIANTABLESIZE
        acc_medianTable1Z = [1] * self.ACC_MEDIANTABLESIZE
        acc_medianTable2X = [1] * self.ACC_MEDIANTABLESIZE
        acc_medianTable2Y = [1] * self.ACC_MEDIANTABLESIZE
        acc_medianTable2Z = [1] * self.ACC_MEDIANTABLESIZE
        mag_medianTable1X = [1] * self.MAG_MEDIANTABLESIZE
        mag_medianTable1Y = [1] * self.MAG_MEDIANTABLESIZE
        mag_medianTable1Z = [1] * self.MAG_MEDIANTABLESIZE
        mag_medianTable2X = [1] * self.MAG_MEDIANTABLESIZE
        mag_medianTable2Y = [1] * self.MAG_MEDIANTABLESIZE
        mag_medianTable2Z = [1] * self.MAG_MEDIANTABLESIZE

        ################# Compass Calibration values ############
        # Use calibrateBerryIMU.py to get calibration values
        # Calibrating the compass isnt mandatory, however a calibrated
        # compass will result in a more accurate heading values.
        magXmin =  -592
        magYmin =  -312
        magZmin =  -334
        magXmax =  140
        magYmax =  -461
        magZmax =  1009

        counter = 0
        while True:
            #Read the accelerometer,gyroscope and magnetometer values
            ACCx = readACCx()
            ACCy = readACCy()
            ACCz = readACCz()
            GYRx = readGYRx()
            GYRy = readGYRy()
            GYRz = readGYRz()
            MAGx = readMAGx()
            MAGy = readMAGy()
            MAGz = readMAGz()


            #Apply compass calibration
            MAGx -= (magXmin + magXmax) /2
            MAGy -= (magYmin + magYmax) /2
            MAGz -= (magZmin + magZmax) /2


            ##Calculate loop Period(LP). How long between Gyro Reads
            b = datetime.datetime.now() - a
            a = datetime.datetime.now()
            LP = b.microseconds/(1000000*1.0)


            #Convert Gyro raw to degrees per second
            rate_gyr_x =  GYRx * self.G_GAIN
            rate_gyr_y =  GYRy * self.G_GAIN
            rate_gyr_z =  GYRz * self.G_GAIN


            #Calculate the angles from the gyro.
            gyroXangle+=rate_gyr_x*LP
            gyroYangle+=rate_gyr_y*LP
            gyroZangle+=rate_gyr_z*LP

            ##Convert Accelerometer values to degrees
            AccXangle =  (math.atan2(ACCy,ACCz)+self.M_PI)*self.RAD_TO_DEG
            AccYangle =  (math.atan2(ACCz,ACCx)+self.M_PI)*self.RAD_TO_DEG


            ####################################################################
            ######################Correct rotation value########################
            ####################################################################
            #Change the rotation value of the accelerometer to -/+ 180 and
            #move the Y axis '0' point to up.
            #
            #Two different pieces of code are used depending on how your IMU is mounted.
            #If IMU is up the correct way, Skull logo is facing down, Use these lines
            AccXangle -= 180.0
            if AccYangle > 90:
                AccYangle -= 270.0
            else:
                AccYangle += 90.0
            #
            #
            #
            #
            #If IMU is upside down E.g Skull logo is facing up;
            #if AccXangle >180:
                #        AccXangle -= 360.0
            #AccYangle-=90
            #if (AccYangle >180):
                #        AccYangle -= 360.0
            ############################ END ##################################


            #Complementary filter used to combine the accelerometer and gyro values.
            CFangleX=self.AA*(CFangleX+rate_gyr_x*LP) +(1 - self.AA) * AccXangle
            CFangleY=self.AA*(CFangleY+rate_gyr_y*LP) +(1 - self.AA) * AccYangle

            #Kalman filter used to combine the accelerometer and gyro values.
            kalmanY = self.kalmanFilterY(AccYangle, rate_gyr_y,LP)
            kalmanX = self.kalmanFilterX(AccXangle, rate_gyr_x,LP)


            ####################################################################
            ############################MAG direction ##########################
            ####################################################################
            #If IMU is upside down, then use this line.  It isnt needed if the
            # IMU is the correct way up
            #MAGy = -MAGy
            #
            ############################ END ##################################


            #Calculate heading
            heading = 180 * math.atan2(MAGy,MAGx)/self.M_PI

            #Only have our heading between 0 and 360
            if heading < 0:
                heading += 360



            ####################################################################
            ###################Tilt compensated heading#########################
            ####################################################################
            #Normalize accelerometer raw values.
            accXnorm = ACCx/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)
            accYnorm = ACCy/math.sqrt(ACCx * ACCx + ACCy * ACCy + ACCz * ACCz)

            #Calculate pitch and roll
            #Use these two lines when the IMU is up the right way. Skull logo is facing down
            pitch = math.asin(accXnorm)
            roll = -math.asin(accYnorm/math.cos(pitch))

            #Calculate the new tilt compensated values
            magXcomp = MAGx*math.cos(pitch)+MAGz*math.sin(pitch)

            magYcomp = MAGx*math.sin(roll)*math.sin(pitch)+MAGy*math.cos(roll)-MAGz*math.sin(roll)*math.cos(pitch)   #LSM9DS0

            #Calculate tilt compensated heading
            tiltCompensatedHeading = -180 * math.atan2(magYcomp,magXcomp)/self.M_PI
            tiltCompensatedHeading = tiltCompensatedHeading-initialHeading


            if tiltCompensatedHeading < 0:
                tiltCompensatedHeading += 360

            if tiltCompensatedHeading < 0:
                tiltCompensatedHeading += 360

            if tiltCompensatedHeading > 180:
                tiltCompensatedHeading -= 360

            #slow program down a bit, makes the output more readable
            counter = counter +1

            if counter >= 20:
                return tiltCompensatedHeading
