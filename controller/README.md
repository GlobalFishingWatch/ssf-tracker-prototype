# Micro Controller

The controller runs on an arduino ESP32 running micropython

## Set up the local dev environment
We use micropython to run the code in the arduino, nut we use standard python for development and testing because I haven't figured out how to use unittest properly in micropython.  Ideally we would run all the unitest in micropython on the dev machine so taht we know everything is the same as it will be on the arduino. 

### Python setup for osx - create a python environment if you don't aleady have one
```
conda create -n py311 python=3.11.4 
conda avtivate py311
```

### Create a python virtualenv
```console
pip install virtualenv
cd controller
virtualenv venv
source venv/bin/activate
pip install -r requirements-dev.txt 
```

### Run the unit tests
```console
python -m unittest app/test_*
```




## SOME RANDOM NOTES BELOW

On OSX, install micropython from source
https://docs.micropython.org/en/latest/develop/gettingstarted.html#building-the-unix-port-of-micropython

Create a dev virutalenv
```
virtualenv venv
venv/bin/activate
pip install -r requirements-dev.txt 
```

How to create a virtual env using micropython (not working?)
```
ln -s /Users/paul/github/micropython/ports/unix/build-standard/micropython /usr/local/bin/micropython
micropython -m mip install venv
source venv-mpy/bin/activate 
```

DONT NEED THIS - CANT RUN UNIT TESTS in micropython anyway
Install micropython unittest tools
```
micropython -m mip install unittest
```

Running unit tests 
```
python -m unittest app/test*
```

Some things for setup with the ESP32-S3

https://micropython.org/download/GENERIC_S3/

```
pip install esptool

esptool.py --chip esp32-S3 --port /dev/tty.usbmodem101 erase_flash
esptool.py --chip esp32s3 --port /dev/tty.usbmodem101 write_flash -z 0 ~/Downloads/GENERIC_S3-20230426-v1.20.0.bin 
```

### Using Thonny IDE to run python code on the ESP hardware

### Monitor the serial port directly from OSX

1. Connect the usb cable to the COM port (not the USB port)

2. find the device name
```
ls /dev/cu*
```
3. should look something like this
```
/dev/cu.usbmodem56292549741
```
4. then connect with screen
```
screen /dev/cu.usbmodem56292549741 115200
```
5. To exit screen, do ctrl-a and then k to kill the session


### set up mpy-utils for direct file system access
github: https://github.com/nickzoic/mpy-utils
```
pip install mpy-utils
```


