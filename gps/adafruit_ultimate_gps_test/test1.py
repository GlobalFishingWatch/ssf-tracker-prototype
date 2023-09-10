# Test1: Connect to the GPS and make sure that it can fix a location

from machine import UART
import utime as time

import adafruit_gps

# Create a GPS module instance.
# Serial will be on Pins 9 and 10
uart = UART(1, baudrate=9600)

# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)

# Turn on the basic GGA and RMC info (what you typically want)
# gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Turn on just minimum info (RMC only, location):
gps.send_command('PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command('PMTK220,1000')

while True:
    gps.update(echo=True)