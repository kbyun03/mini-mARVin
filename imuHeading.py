import serial
import time
import sys
import math
import IMU
import datetime
import os
from threading import Thread

class ImuPosHeading():
	def __init__(self):
		RAD_TO_DEG = 57.29578
		M_PI = 3.14159265358979323846
		G_GAIN = 0.070  	# [deg/s/LSB]  If you change the dps for gyro, you need to update this value accordingly
		AA =  0.40      	# Complementary filter constant
		MAG_LPF_FACTOR = 0.4 	# Low pass filter constant magnetometer
		ACC_LPF_FACTOR = 0.4 	# Low pass filter constant for accelerometer
		ACC_MEDIANTABLESIZE = 9    	# Median filter table size for accelerometer. Higher = smoother but a longer delay
		MAG_MEDIANTABLESIZE = 9    	# Median filter table size for magnetometer. Higher = smoother but a longer delay

		#Kalman filter variables
		Q_angle = 0.02
		Q_gyro = 0.0015
		R_angle = 0.005
		y_bias = 0.0
		x_bias = 0.0
		XP_00 = 0.0
		XP_01 = 0.0
		XP_10 = 0.0
		XP_11 = 0.0
		YP_00 = 0.0
		YP_01 = 0.0
		YP_10 = 0.0
		YP_11 = 0.0
		KFangleX = 0.0
		KFangleY = 0.0


	def kalmanFilterY ( self,accAngle, gyroRate, DT):
		y=0.0
		S=0.0

		KFangleY = KFangleY + DT * (gyroRate - y_bias)

		YP_00 = YP_00 + ( - DT * (YP_10 + YP_01) + Q_angle * DT )
		YP_01 = YP_01 + ( - DT * YP_11 )
		YP_10 = YP_10 + ( - DT * YP_11 )
		YP_11 = YP_11 + ( + Q_gyro * DT )

		y = accAngle - KFangleY
		S = YP_00 + R_angle
		K_0 = YP_00 / S
		K_1 = YP_10 / S

		KFangleY = KFangleY + ( K_0 * y )
		y_bias = y_bias + ( K_1 * y )

		YP_00 = YP_00 - ( K_0 * YP_00 )
		YP_01 = YP_01 - ( K_0 * YP_01 )
		YP_10 = YP_10 - ( K_1 * YP_00 )
		YP_11 = YP_11 - ( K_1 * YP_01 )

		return KFangleY

	def kalmanFilterX ( self,accAngle, gyroRate, DT):
		x=0.0
		S=0.0

		KFangleX = KFangleX + DT * (gyroRate - x_bias)

		XP_00 = XP_00 + ( - DT * (XP_10 + XP_01) + Q_angle * DT )
		XP_01 = XP_01 + ( - DT * XP_11 )
		XP_10 = XP_10 + ( - DT * XP_11 )
		XP_11 = XP_11 + ( + Q_gyro * DT )

		x = accAngle - KFangleX
		S = XP_00 + R_angle
		K_0 = XP_00 / S
		K_1 = XP_10 / S

		KFangleX = KFangleX + ( K_0 * x )
		x_bias = x_bias + ( K_1 * x )

		XP_00 = XP_00 - ( K_0 * XP_00 )
		XP_01 = XP_01 - ( K_0 * XP_01 )
		XP_10 = XP_10 - ( K_1 * XP_00 )
		XP_11 = XP_11 - ( K_1 * XP_01 )

		return KFangleX

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
		acc_medianTable1X = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable1Y = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable1Z = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2X = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2Y = [1] * ACC_MEDIANTABLESIZE
		acc_medianTable2Z = [1] * ACC_MEDIANTABLESIZE
		mag_medianTable1X = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable1Y = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable1Z = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2X = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2Y = [1] * MAG_MEDIANTABLESIZE
		mag_medianTable2Z = [1] * MAG_MEDIANTABLESIZE

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
			ACCx = IMU.readACCx()
			ACCy = IMU.readACCy()
			ACCz = IMU.readACCz()
			GYRx = IMU.readGYRx()
			GYRy = IMU.readGYRy()
			GYRz = IMU.readGYRz()
			MAGx = IMU.readMAGx()
			MAGy = IMU.readMAGy()
			MAGz = IMU.readMAGz()


			#Apply compass calibration
			MAGx -= (magXmin + magXmax) /2
			MAGy -= (magYmin + magYmax) /2
			MAGz -= (magZmin + magZmax) /2


			##Calculate loop Period(LP). How long between Gyro Reads
			b = datetime.datetime.now() - a
			a = datetime.datetime.now()
			LP = b.microseconds/(1000000*1.0)


			#Convert Gyro raw to degrees per second
			rate_gyr_x =  GYRx * G_GAIN
			rate_gyr_y =  GYRy * G_GAIN
			rate_gyr_z =  GYRz * G_GAIN


			#Calculate the angles from the gyro.
			gyroXangle+=rate_gyr_x*LP
			gyroYangle+=rate_gyr_y*LP
			gyroZangle+=rate_gyr_z*LP

			##Convert Accelerometer values to degrees
			AccXangle =  (math.atan2(ACCy,ACCz)+M_PI)*RAD_TO_DEG
			AccYangle =  (math.atan2(ACCz,ACCx)+M_PI)*RAD_TO_DEG


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
			CFangleX=AA*(CFangleX+rate_gyr_x*LP) +(1 - AA) * AccXangle
			CFangleY=AA*(CFangleY+rate_gyr_y*LP) +(1 - AA) * AccYangle

			#Kalman filter used to combine the accelerometer and gyro values.
			kalmanY = kalmanFilterY(AccYangle, rate_gyr_y,LP)
			kalmanX = kalmanFilterX(AccXangle, rate_gyr_x,LP)


			####################################################################
			############################MAG direction ##########################
			####################################################################
			#If IMU is upside down, then use this line.  It isnt needed if the
			# IMU is the correct way up
			#MAGy = -MAGy
			#
			############################ END ##################################


			#Calculate heading
			heading = 180 * math.atan2(MAGy,MAGx)/M_PI

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
			tiltCompensatedHeading = -180 * math.atan2(magYcomp,magXcomp)/M_PI
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
