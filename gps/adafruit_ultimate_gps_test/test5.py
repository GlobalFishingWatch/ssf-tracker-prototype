# Test2: Turn the GPS on and off with the EN pin

from machine import UART
from machine import Pin
from machine import Timer
import utime as time

import adafruit_gps

enable_pin = Pin(8, Pin.OUT)

# Create a GPS module instance.
# Serial will be on Pins 9 and 10
uart = UART(1, baudrate=9600)

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)

def tick(timer):
    gps.update(echo=True)

# Turn on the basic GGA and RMC info (what you typically want)
# gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Turn on just minimum info (RMC only, location):
gps.send_command('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command('PMTK220,1000')

timer = Timer(1)
timer.init(period=100, mode=Timer.PERIODIC, callback=tick)

gps.send_command('PMTK225,0')  # reset periodic mode
gps.send_command('PMTK223,1,25,180000,60000') # timing for collecting ephemeris
# gps.send_command('PMTK225,1,3000,12000,18000,72000')    # start periodic backup mode
# gps.send_command('PMTK225,2,3000,12000,18000,72000')    # start periodic standby mode
gps.send_command('PMTK225,4,3000,12000,18000,72000')    # start perpetual backup mode

gps.send_command('PMTK187,1,60')  # locus fix interval in seconds
gps.send_command('PMTK185,0')     # start logging