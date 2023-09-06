import time
#from boot import gps
from util import RGB
from boot import color


class Satellite():
    def send_log(self, loc_array):
        for x in range(4):
            color.setColor("white")
            time.sleep(.1)
            color.setColor("yellow")
            time.sleep(.1)  
