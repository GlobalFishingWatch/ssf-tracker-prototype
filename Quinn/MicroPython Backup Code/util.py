from machine import Pin
import neopixel


class RGB:
    
    def __init__(self):
        self.rgb = neopixel.NeoPixel(Pin(0), 1)
        self.np_power = Pin(2, Pin.OUT)
        self.np_power.on()
        
        
    def setColor(self, color):
        colors = {
            "red" : (20, 0, 0),
            "blue" : (0, 0, 20),
            "green" : (0, 20, 0),
            "yellow" : (20, 20, 0),
            "off": (0, 0, 0),
            "white": (20, 20, 20)
        }
        self.rgb.fill(colors[color])
        self.rgb.write()
    
    
#Function to add argument given to the log file
def log(arg):
    log_filename = 'lib/log_file.log'
        
    with open(log_filename, 'a') as log_file:
        log_file.write(arg)
