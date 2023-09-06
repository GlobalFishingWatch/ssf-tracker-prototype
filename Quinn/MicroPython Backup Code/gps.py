import adafruit_gps
import time
import os
from util import RGB
from machine import UART
from boot import color


class GPS:
    #Constructor for GPS class - Initializes starting time
    def __init__(self, tx_pin, rx_pin, baudrate, config):
        
        uart = UART(1, baudrate)
        
        # Create a GPS module instance.
        self.gps = adafruit_gps.GPS(uart)

        # Turn on the basic GGA and RMC info (what you typically want)
        self.gps.send_command('PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')

        # Set update rate to once a second (1hz) which is what you typically want.
        self.gps.send_command('PMTK220,1000')
        
        #Set config
        self.config = config
    
    # Retreive GPS data and store it
    def logLocation(self):
        loc = self.getLocation()
        logFile = open("lib/locations.log", "a")
        logFile.write(loc + "\n")
        logFile.close()
    
    # Return previous stored locations
    def readLocations(self):
        loc_array = []
        logFile = open("lib/locations.log", "r")
        
        
        for line in logFile:
            loc_array.append(line.strip())
            
        logFile.close()
        return loc_array.copy()
    
    #Deletes log file if exists
    def delete_log_file(self):
        os.remove("lib/locations.log")
        color.setColor("white")
        time.sleep(.2)
    
    #Returns # of lines in the log file
    def count_lines(self):
        lineCount = 0
        logFile = open("lib/locations.log", "r")
        for line in logFile:
            lineCount += 1
        logFile.close()
        return lineCount
            
    #Return current location
    def getLocation(self):
        start_time = time.ticks_ms()
        last_check = start_time
        while True:
            # Make sure to call gps.update() every loop iteration and at least twice
            # as fast as data comes from the GPS unit (usually every second).
            # This returns a bool that's true if it parsed new data (you can ignore it
            # though if you don't care and instead look at the has_fix property).
            self.gps.update()
            # Every second print out current location details if there's a fix.
            
            current = time.ticks_ms()
            if time.ticks_diff(last_check, current) >= 1000:
                last_check = current
                if not self.gps.has_fix:
                    print("GPS has no fix")
                else:
                    #gps.has_fix is true(We have a fix)
                    # Return time and location
                    return (("D-{day} T-{h:02}:{m:02}:{s:02} Latitude:{lat} degrees Longitude: {long} degrees").format(
                        day=self.gps.timestamp_utc.tm_mday, h=self.gps.timestamp_utc.tm_hour,
                        m=self.gps.timestamp_utc.tm_min, s=self.gps.timestamp_utc.tm_sec,
                        lat=self.gps.latitude, long=self.gps.longitude))
                
            if current - start_time >= self.config["gps_timeout"]:
                return "GPS fix not found"
                
    # Test function that prints GPS sentence parsed
    def printLocation(self):
        print(self.getLocation())