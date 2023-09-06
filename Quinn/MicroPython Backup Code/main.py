# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()

import machine
import esp32
import neopixel
from util import RGB
import time
from satellite import Satellite
from gps import GPS
from util import log
from machine import deepsleep
from micropython import schedule
import json
import boot


# Function to handle setup mode
def setup_mode():
    color.setColor("green")
    time.sleep(3)
    color.setColor("off")
    
# Function to handle SOS mode
def sos():
    for x in range(5):
        color.setColor("red")
        time.sleep(1)
        color.setColor("off")

def main():
    print(wake_msg())
    
    color.setColor("white")
    time.sleep(2)
    color.setColor("off")
    
    # Load config
    # default values
    config = {'gps_timeout': 10}
    
    # Create an instance of the Satellite and GPS class
    sat = Satellite()
    gps = GPS(8, 7, 38400, config)

    cfg_filename = 'lib/config2.json'
    try:
        # try to load the file
        with open(cfg_filename, 'r') as cfg_file:
            config.update(json.load(cfg_file))
    except OSError:
        # file doesn't exist, so create it
        with open(cfg_filename, 'w') as cfg_file:
              json.dump(config, cfg_file)

    # Determine wakeup reason
    # If reason is sos button, enter SOS mode
    # If reason is setup button, enter setup
    '''
    triggered_alarm = alarm.wake_alarm
    if triggered_alarm != None and triggered_alarm.pin:
        if triggered_alarm.pin == sos_pin_alarm:
            log()
        elif triggered_alarm.pin == setup_pin_alarm:
            setup_mode()
    '''

    color.setColor("off")
    gps.logLocation()
    print("Location Logged")
    print(gps.count_lines())

    if gps.count_lines() >= max_lines:
        print(gps.count_lines())
        #setColor("yellow")
        #time.sleep(5)
        sat.send_log(gps.readLocations())
        gps.delete_log_file()


    # Indicate machine is going to sleep and sleep(in milliseconds)
    # https://randomnerdtutorials.com/micropython-esp32-deep-sleep-wake-up-sources/
    color.setColor("red")
    time.sleep(.2)
    color.setColor("blue")
    #Set sleep alarm

    #write out the config file before we go to sleep
    with open(cfg_filename, 'w') as cfg_file:
        json.dump(config, cfg_file)
        
    #Deep sleep for x/1000 seconds
    #alarm.exit_and_deep_sleep_until_alarms(time_alarm, sos_pin_alarm, setup_pin_alarm)
    deepsleep(5000)
    
    
try:
    main()
except OSError:
    log("OS Error")