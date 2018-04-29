#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gpiozero.input_devices import DigitalInputDevice
from gpiozero.output_devices import DigitalOutputDevice
import warnings
from time import sleep, time
from threading import Event, Lock
##try:
##    from statistics import median
##except ImportError:
##    from .compat import median

from gpiozero.exc import InputDeviceError, DeviceClosed, DistanceSensorNoEcho
from gpiozero.devices import GPIODevice
from gpiozero.mixins import GPIOQueue, EventsMixin, HoldMixin


class DistanceSensor():
    """
    Extends :class:`SmoothedInputDevice` and represents an HC-SR04 ultrasonic
    distance sensor, as found in the `CamJam #3 EduKit`_.

    The distance sensor requires two GPIO pins: one for the *trigger* (marked
    TRIG on the sensor) and another for the *echo* (marked ECHO on the sensor).
    However, a voltage divider is required to ensure the 5V from the ECHO pin
    doesn't damage the Pi. Wire your sensor according to the following
    instructions:

    1. Connect the GND pin of the sensor to a ground pin on the Pi.

    2. Connect the TRIG pin of the sensor a GPIO pin.

    3. Connect one end of a 330Ω resistor to the ECHO pin of the sensor.

    4. Connect one end of a 470Ω resistor to the GND pin of the sensor.

    5. Connect the free ends of both resistors to another GPIO pin. This forms
       the required `voltage divider`_.

    6. Finally, connect the VCC pin of the sensor to a 5V pin on the Pi.

    .. note::

        If you do not have the precise values of resistor specified above,
        don't worry! What matters is the *ratio* of the resistors to each
        other.

        You also don't need to be absolutely precise; the `voltage divider`_
        given above will actually output ~3V (rather than 3.3V). A simple 2:3
        ratio will give 3.333V which implies you can take three resistors of
        equal value, use one of them instead of the 330Ω resistor, and two of
        them in series instead of the 470Ω resistor.

    .. _voltage divider: https://en.wikipedia.org/wiki/Voltage_divider

    The following code will periodically report the distance measured by the
    sensor in cm assuming the TRIG pin is connected to GPIO17, and the ECHO
    pin to GPIO18::

        from gpiozero import DistanceSensor
        from time import sleep

        sensor = DistanceSensor(echo=18, trigger=17)
        while True:
            print('Distance: ', sensor.distance * 100)
            sleep(1)

    :param int echo:
        The GPIO pin which the ECHO pin is attached to. See
        :ref:`pin-numbering` for valid pin numbers.

    :param int trigger:
        The GPIO pin which the TRIG pin is attached to. See
        :ref:`pin-numbering` for valid pin numbers.

    :param int queue_len:
        The length of the queue used to store values read from the sensor.
        This defaults to 30.

    :param float max_distance:
        The :attr:`value` attribute reports a normalized value between 0 (too
        close to measure) and 1 (maximum distance). This parameter specifies
        the maximum distance expected in meters. This defaults to 1.

    :param float threshold_distance:
        Defaults to 0.3. This is the distance (in meters) that will trigger the
        ``in_range`` and ``out_of_range`` events when crossed.

    :param bool partial:
        When ``False`` (the default), the object will not return a value for
        :attr:`~SmoothedInputDevice.is_active` until the internal queue has
        filled with values.  Only set this to ``True`` if you require values
        immediately after object construction.

    :param Factory pin_factory:
        See :doc:`api_pins` for more information (this is an advanced feature
        which most users can ignore).

    .. _CamJam #3 EduKit: http://camjam.me/?page_id=1035
    """

    def __init__( self, echo=None, trigger=None):
        self.trigger = DigitalOutputDevice(trigger)
        self.echo = DigitalInputDevice(echo, pull_up=False)
        self.speed_of_sound = 34326 # m/s

    @property
    def distance(self):
        """
        Returns the current distance measured by the sensor in meters. Note
        that this property will have a value between 0 and
        :attr:`max_distance`.
        """
        return self._read()


    def _read(self):
        # Make sure the echo pin is low then ensure the echo event is clear
        while self.echo.is_active:
            sleep(0.00001)
        # Obtain ECHO_LOCK to ensure multiple distance sensors don't listen
        # for each other's "pings"
        # Fire the trigger
        dist = []
##        for i in range(0,11):
        self.trigger.on()
        sleep(0.00001)
        self.trigger.off()

        StartTime = time()
        StopTime = time()
        
        while(self.echo.is_active == False):
            StartTime = time()
        while(self.echo.is_active == True):
            StopTime = time()
        TimeElapsed = StopTime - StartTime
        distance = (TimeElapsed *34326) / 2
        dist.append(distance)
       

        
        
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
